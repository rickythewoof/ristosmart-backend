from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Order, OrderItem, MenuItem
from auth import permission_required, role_required, authentication_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta
import uuid

from models import Order, OrderItem, MenuItem


order_bp = Blueprint('orders', __name__)

class OrderItemSchema(Schema):
    menu_item_id = fields.Str(required=True)
    quantity = fields.Int(required=True, validate=lambda x: x > 0)
    special_instructions = fields.Str(allow_none=True)

    class Meta(Schema.Meta):
        unknown = 'exclude'

class OrderSchema(Schema):
    table_number = fields.Int(required=True, validate=lambda x: x > 0)
    customer_name = fields.Str(allow_none=True)
    order_type = fields.Str(required=True, validate=lambda x: x in ['dine_in', 'takeout', 'delivery'])
    special_instructions = fields.Str(allow_none=True)
    total_amount = fields.Float(allow_none=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=lambda x: len(x) > 0)

    class Meta(Schema.Meta):
        unknown = 'exclude'

order_schema = OrderSchema()


def generate_order_number():
    """Generate a unique order number"""
    import random
    prefix = datetime.now().strftime("%Y%m%d")
    suffix = random.randint(1000, 9999)
    return f"ORD-{prefix}-{suffix}"


def calculate_estimated_completion_time(items):
    """Calculate estimated completion time based on preparation times"""
    from models import italy_now
    max_prep_time = max([item.get('preparation_time', 15) for item in items], default=15)
    estimated_minutes = max_prep_time + 5
    return italy_now() + timedelta(minutes=estimated_minutes)


# ============ PUBLIC/PROTECTED ENDPOINTS ============

@order_bp.route('/', methods=['GET'])
@authentication_required()
def get_all_orders():
    """Get all orders with optional filtering - PROTECTED"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        status = request.args.get('status')
        table_number = request.args.get('table_number')
        order_type = request.args.get('order_type')
        
        query = Order.query
        
        if status:
            if status == 'active':
                query = query.filter(Order.status.in_(['pending', 'confirmed', 'preparing']))
            else:
                query = query.filter(Order.status == status)
        
        if table_number:
            query = query.filter(Order.table_number == int(table_number))
        
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders],
            'count': len(orders),
            'fetched_by_role': user_role
        })
        
    except Exception as e:
        print(f"Error in get_all_orders: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching orders',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
def get_order_by_id(order_id):
    """Get order by ID - PROTECTED"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict()
        })
        
    except Exception as e:
        print(f"Error in get_order_by_id: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching order',
            'error': str(e)
        }), 500


@order_bp.route('/', methods=['POST'])
@permission_required('order.create')
def create_order():
    """Create a new order - PROTECTED: Waiter, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        data = request.json
        print(f"[AUDIT] Order creation by {user_role} {user_id}: {data}")
        
        try:
            validated_data = order_schema.load(data)
        except ValidationError as err:
            print(f"Validation error: {err.messages}")
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        # Verify menu items availability
        menu_item_ids = [item['menu_item_id'] for item in validated_data['items']]
        available_items = MenuItem.query.filter(
            MenuItem.id.in_(menu_item_ids),
            MenuItem.is_available == True
        ).all()
        
        available_ids = {item.id for item in available_items}
        unavailable_items = [mid for mid in menu_item_ids if mid not in available_ids]
        
        if unavailable_items:
            return jsonify({
                'success': False,
                'message': 'Some menu items are not available',
                'unavailable_items': unavailable_items
            }), 400
        
        # Calculate totals by fetching the prices from the db and multiplying by quantity
        for item in validated_data['items']:
            menu_item = next((mi for mi in available_items if mi.id == item['menu_item_id']), None)
            if menu_item:
                item['menu_item_name'] = menu_item.name
                item['unit_price'] = float(menu_item.price)
                item['total_price'] = (float(menu_item.price) * item['quantity']) * \
                    (1 + (menu_item.tax_amount if menu_item.tax_amount else 0))


        total_amount = sum(item['total_price'] for item in validated_data['items'])
        discount_amount = 0 # Can be extended to apply discounts
        final_amount = total_amount - discount_amount
        
        # Create order
        order = Order(
            order_number=generate_order_number(),
            table_number=validated_data['table_number'],
            customer_name=validated_data.get('customer_name'),
            order_type=validated_data['order_type'],
            status='confirmed',
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            special_instructions=validated_data.get('special_instructions'),
            estimated_completion_time=calculate_estimated_completion_time(validated_data['items'])
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        for item_data in validated_data['items']:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data['menu_item_id'],
                menu_item_name=item_data['menu_item_name'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                special_instructions=item_data.get('special_instructions'),
                status='preparing'
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        print(f"[AUDIT] Order {order.order_number} created by {user_role} {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'data': order.to_dict(),
            'created_by': {'role': user_role}
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database integrity error',
            'error': str(e.orig) if hasattr(e, 'orig') else str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error creating order',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>/status', methods=['PUT'])
@permission_required('order.update_status')
def update_order_status(order_id):
    """Update order status - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        try:
            uuid.UUID(order_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid order ID format'
            }), 400
        
        result = db.session.execute(
            text("SELECT * FROM orders WHERE id = :order_id"),
            {'order_id': order_id}
        ).fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'payed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        print(f"[AUDIT] Order {order_id} status changed to {new_status} by {user_role}")
        
        db.session.execute(
            text("UPDATE orders SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :order_id"),
            {'status': new_status, 'order_id': order_id}
        )
        
        if new_status in ['preparing', 'ready', 'delivered']:
            db.session.execute(
                text("""
                    UPDATE order_items 
                    SET status = :item_status, updated_at = CURRENT_TIMESTAMP 
                    WHERE order_id = :order_id AND status = 'pending'
                """),
                {'item_status': new_status if new_status != 'confirmed' else 'pending', 'order_id': order_id}
            )
        
        db.session.commit()
        
        updated_order = Order.query.get(order_id)
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'data': updated_order.to_dict(),
            'updated_by_role': user_role
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_order_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error updating order status',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>/items/<string:item_id>/status', methods=['PUT'])
@permission_required('order.update_status')
def update_order_item_status(order_id, item_id):
    """Update order item status - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        try:
            uuid.UUID(order_id)
            uuid.UUID(item_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        order_result = db.session.execute(
            text("SELECT * FROM orders WHERE id = :order_id"),
            {'order_id': order_id}
        ).fetchone()
        
        if not order_result:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        item_result = db.session.execute(
            text("SELECT * FROM order_items WHERE id = :item_id AND order_id = :order_id"),
            {'item_id': item_id, 'order_id': order_id}
        ).fetchone()
        
        if not item_result:
            return jsonify({
                'success': False,
                'message': 'Order item not found'
            }), 404
        
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        valid_statuses = ['pending', 'preparing', 'ready', 'served', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        print(f"[AUDIT] Order item {item_id} status changed to {new_status} by {user_role}")
        
        db.session.execute(
            text("""
                UPDATE order_items 
                SET status = :status, updated_at = CURRENT_TIMESTAMP 
                WHERE id = :item_id AND order_id = :order_id
            """),
            {'status': new_status, 'item_id': item_id, 'order_id': order_id}
        )
        
        # Check if all items are ready
        all_items_result = db.session.execute(
            text("""
                SELECT COUNT(*) as total_count,
                       COUNT(CASE WHEN status IN ('ready', 'served') THEN 1 END) as ready_count
                FROM order_items 
                WHERE order_id = :order_id
            """),
            {'order_id': order_id}
        ).fetchone()
        
        if all_items_result.total_count == all_items_result.ready_count and order_result.status != 'ready':
            db.session.execute(
                text("UPDATE orders SET status = 'ready', updated_at = CURRENT_TIMESTAMP WHERE id = :order_id"),
                {'order_id': order_id}
            )
        
        db.session.commit()
        
        updated_order = Order.query.get(order_id)
        
        return jsonify({
            'success': True,
            'message': 'Order item status updated successfully',
            'data': updated_order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_order_item_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error updating order item status',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>/pay', methods=['POST'])
@permission_required('order.update_payment')
def pay_order(order_id):
    """Process payment for order - PROTECTED: Cashier, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        try:
            uuid.UUID(order_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid order ID format'
            }), 400
        
        result = db.session.execute(
            text("SELECT * FROM orders WHERE id = :order_id"),
            {'order_id': order_id}
        ).fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        if result.status not in ['ready', 'delivered']:
            return jsonify({
                'success': False,
                'message': f'Order must be ready or delivered to be paid. Current status: {result.status}'
            }), 400
        
        data = request.json or {}
        payment_method = data.get('payment_method', 'cash')
        payment_amount = data.get('payment_amount')
        
        if payment_amount is not None:
            try:
                payment_amount = float(payment_amount)
                if payment_amount < float(result.final_amount):
                    return jsonify({
                        'success': False,
                        'message': f'Payment amount (€{payment_amount}) is less than order total (€{result.final_amount})'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid payment amount'
                }), 400
        
        print(f"[AUDIT] Payment processed for order {order_id} by {user_role} {user_id} - Method: {payment_method}")
        
        db.session.execute(
            text("UPDATE orders SET status = 'payed', updated_at = CURRENT_TIMESTAMP WHERE id = :order_id"),
            {'order_id': order_id}
        )
        
        db.session.commit()
        
        updated_order = Order.query.get(order_id)
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'data': updated_order.to_dict(),
            'payment_info': {
                'method': payment_method,
                'amount': float(result.final_amount),
                'change': payment_amount - float(result.final_amount) if payment_amount else 0,
                'processed_by_role': user_role
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in pay_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error processing payment',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>', methods=['DELETE'])
@role_required('manager')
def delete_order(order_id):
    """Delete order - PROTECTED: Manager only"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        if order.status not in ['pending', 'cancelled']:
            return jsonify({
                'success': False,
                'message': 'Can only delete pending or cancelled orders'
            }), 400
        
        order_number = order.order_number
        
        print(f"[AUDIT] Order {order_number} deleted by manager {user_id}")
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error deleting order',
            'error': str(e)
        }), 500
