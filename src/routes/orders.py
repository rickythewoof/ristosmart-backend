from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from flasgger import swag_from
from docs.order_docs import (
    get_all_orders_spec,
    get_order_spec,
    create_order_spec,
    update_order_status_spec,
    update_order_item_status_spec,
    process_payment_spec,
    delete_order_spec
)
from models import db, Order, OrderItem, MenuItem
from auth import permission_required, role_required, authentication_required
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta
import uuid

order_bp = Blueprint('orders', __name__)

class OrderItemSchema(Schema):
    id = fields.Str(dump_only=True)
    menu_item_id = fields.Str(required=True)
    menu_item_name = fields.Str(dump_only=True)
    quantity = fields.Int(required=True, validate=lambda x: x > 0)
    unit_price = fields.Float(dump_only=True)
    total_price = fields.Float(dump_only=True)
    special_instructions = fields.Str(allow_none=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = 'exclude'

class OrderSchema(Schema):
    id = fields.Str(dump_only=True)
    order_number = fields.Str(dump_only=True)
    table_number = fields.Int(required=True, validate=lambda x: x > 0)
    customer_name = fields.Str(allow_none=True)
    order_type = fields.Str(required=True, validate=lambda x: x in ['dine_in', 'takeout', 'delivery'])
    status = fields.Str(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    tax_amount = fields.Float(dump_only=True)
    discount_amount = fields.Float(dump_only=True)
    final_amount = fields.Float(dump_only=True)
    special_instructions = fields.Str(allow_none=True)
    estimated_completion_time = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=lambda x: len(x) > 0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = 'exclude'

class OrderStatusUpdateSchema(Schema):
    status = fields.Str(required=True, validate=lambda x: x in ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'payed', 'cancelled'])

class OrderItemStatusUpdateSchema(Schema):
    status = fields.Str(required=True, validate=lambda x: x in ['pending', 'preparing', 'ready', 'served', 'cancelled'])

class PaymentSchema(Schema):
    payment_method = fields.Str(missing='cash')
    payment_amount = fields.Float(allow_none=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_status_update_schema = OrderStatusUpdateSchema()
order_item_status_update_schema = OrderItemStatusUpdateSchema()
payment_schema = PaymentSchema()


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
@swag_from(get_all_orders_spec)
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
            'data': orders_schema.dump(orders),
            'count': len(orders)
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_orders: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching orders',
            'error': str(e)
        }), 500


@order_bp.route('/<string:order_id>', methods=['GET'])
@jwt_required()
@swag_from(get_order_spec)
def get_order_by_id(order_id):
    """Get order by ID - PROTECTED"""
    try:
        # Validate UUID
        try:
            uuid.UUID(order_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid order ID format'
            }), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': order_schema.dump(order)
        }), 200
        
    except Exception as e:
        print(f"Error in get_order_by_id: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error fetching order',
            'error': str(e)
        }), 500


@order_bp.route('/', methods=['POST'])
@permission_required('order.create')
@swag_from(create_order_spec)
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
            'data': order_schema.dump(order)
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
@swag_from(update_order_status_spec)
def update_order_status(order_id):
    """Update order status - PROTECTED: Chef, Manager"""
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
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        try:
            data = order_status_update_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        new_status = data['status']
        
        print(f"[AUDIT] Order {order_id} status changed to {new_status} by {user_role} {user_id}")
        
        order.status = new_status
        
        if new_status in ['preparing', 'ready', 'delivered']:
            item_status = new_status if new_status != 'confirmed' else 'pending'
            for item in order.items:
                if item.status == 'pending':
                    item.status = item_status
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'data': order_schema.dump(order)
        }), 200
        
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
@swag_from(update_order_item_status_spec)
def update_order_item_status(order_id, item_id):
    """Update order item status - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        try:
            uuid.UUID(order_id)
            uuid.UUID(item_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        order_item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first()
        
        if not order_item:
            return jsonify({
                'success': False,
                'message': 'Order item not found'
            }), 404
        
        try:
            data = order_item_status_update_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        new_status = data['status']
        
        print(f"[AUDIT] Order item {item_id} status changed to {new_status} by {user_role} {user_id}")
        
        order_item.status = new_status
        
        all_items_ready = all(item.status in ['ready', 'served'] for item in order.items)
        
        if all_items_ready and order.status != 'ready':
            order.status = 'ready'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order item status updated successfully',
            'data': order_schema.dump(order)
        }), 200
        
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
@swag_from(process_payment_spec)
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
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        if order.status not in ['ready', 'delivered']:
            return jsonify({
                'success': False,
                'message': f'Order must be ready or delivered to be paid. Current status: {order.status}'
            }), 400
        
        try:
            payment_data = payment_schema.load(request.json or {})
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        payment_method = payment_data['payment_method']
        payment_amount = payment_data.get('payment_amount')
        
        if payment_amount is not None:
            if payment_amount < float(order.final_amount):
                return jsonify({
                    'success': False,
                    'message': f'Payment amount (€{payment_amount}) is less than order total (€{order.final_amount})'
                }), 400
        
        print(f"[AUDIT] Payment processed for order {order_id} by {user_role} {user_id} - Method: {payment_method}")
        
        order.status = 'payed'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'data': order_schema.dump(order),
            'payment_info': {
                'method': payment_method,
                'amount': float(order.final_amount),
                'change': payment_amount - float(order.final_amount) if payment_amount else 0
            }
        }), 200
        
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
@swag_from(delete_order_spec)
def delete_order(order_id):
    """Delete order - PROTECTED: Manager only"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        
        try:
            uuid.UUID(order_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid order ID format'
            }), 400
        
        # Find order using ORM
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
        }), 200
        
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
