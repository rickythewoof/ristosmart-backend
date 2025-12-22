from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from models import db, MenuItem
from auth import permission_required, role_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from marshmallow import Schema, fields, ValidationError
import uuid
import json
import psycopg2
import os

menu_bp = Blueprint('menu', __name__)

# Marshmallow schemas for validation
class MenuItemSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 100)
    description = fields.Str(allow_none=True)
    image_url = fields.Str(allow_none=True)
    price = fields.Float(required=True, validate=lambda x: x >= 0)
    tax_amount = fields.Float(allow_none=True, validate=lambda x: x >= 0 and x <=1)
    category = fields.Str(required=True, validate=lambda x: x in ['appetizer', 'main', 'dessert', 'beverage', 'side'])
    is_available = fields.Bool()
    preparation_time = fields.Int(required=True, validate=lambda x: x >= 1)
    allergens = fields.List(fields.Str(), allow_none=True)
    nutritional_info = fields.Dict(allow_none=True)

menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)


def get_db_connection():
    """Get database connection using app config"""
    from flask import current_app
    config = current_app.config
    
    try:
        return psycopg2.connect(
            host=config.get('DB_HOST', 'localhost'),
            port=int(config.get('DB_PORT', '5432')),
            database=config.get('DB_NAME', 'byteristo_db'),
            user=config.get('DB_USER', 'byteristo_user'),
            password=config.get('DB_PASSWORD', 'byteristo_password')
        )
    except Exception as e:
        print(f"Failed to connect using config, trying env vars: {e}")
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'byteristo_db'),
            user=os.getenv('DB_USER', 'byteristo_user'),
            password=os.getenv('DB_PASSWORD', 'byteristo_password')
        )


# ============ PUBLIC ENDPOINTS ============

@menu_bp.route('/', methods=['GET'])
def get_all_menu_items():
    """Get all menu items with optional filtering - PUBLIC"""
    try:
        category = request.args.get('category')
        available = request.args.get('available')
        
        query = MenuItem.query
        
        if category:
            query = query.filter(MenuItem.category == category)
        if available is not None:
            is_available = available.lower() == 'true'
            query = query.filter(MenuItem.is_available == is_available)
        
        menu_items = query.order_by(MenuItem.category, MenuItem.name).all()
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in menu_items],
            'count': len(menu_items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching menu items',
            'error': str(e)
        }), 500


@menu_bp.route('/available', methods=['GET'])
def get_available_menu_items():
    """Get available menu items for ordering - PUBLIC"""
    try:
        menu_items = MenuItem.query.filter(MenuItem.is_available == True).all()
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in menu_items],
            'count': len(menu_items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching available menu items',
            'error': str(e)
        }), 500


@menu_bp.route('/<string:menu_id>', methods=['GET'])
def get_menu_item_by_id(menu_id):
    """Get menu item by ID - PUBLIC"""
    try:
        try:
            uuid.UUID(menu_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid menu item ID format'
            }), 400
        
        result = db.session.execute(
            text("SELECT * FROM menu_items WHERE id = :menu_id"),
            {'menu_id': menu_id}
        ).fetchone()
        
        if not result:
            return jsonify({
                'success': False,
                'message': 'Menu item not found'
            }), 404
        
        row_dict = dict(result._mapping)
        menu_item_dict = {
            'id': row_dict['id'],
            'name': row_dict['name'],
            'description': row_dict['description'],
            'price': float(row_dict['price']) if row_dict['price'] else 0,
            'category': row_dict['category'],
            'is_available': row_dict['is_available'],
            'preparation_time': row_dict['preparation_time'],
            'allergens': json.loads(row_dict['allergens']) if row_dict['allergens'] else [],
            'nutritional_info': json.loads(row_dict['nutritional_info']) if row_dict['nutritional_info'] else {},
            'created_at': row_dict['created_at'].isoformat() if row_dict['created_at'] else None,
            'updated_at': row_dict['updated_at'].isoformat() if row_dict['updated_at'] else None
        }
        
        return jsonify({
            'success': True,
            'data': menu_item_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching menu item',
            'error': str(e)
        }), 500


# ============ PROTECTED ENDPOINTS ============

@menu_bp.route('/', methods=['POST'])
@permission_required('menu.create')
def create_menu_item():
    """Create a new menu item - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        print(f"[AUDIT] Menu item creation attempt by user {user_id} ({user_role})")
        
        try:
            data = menu_item_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        menu_item = MenuItem(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            tax_amount=data.get('tax_amount'),
            category=data['category'],
            is_available=data.get('is_available', True),
            preparation_time=data['preparation_time'],
            allergens=json.dumps(data.get('allergens')) if data.get('allergens') is not None else None,
            nutritional_info=json.dumps(data.get('nutritional_info')) if data.get('nutritional_info') is not None else None
        )
        
        db.session.add(menu_item)
        db.session.commit()
        
        print(f"[AUDIT] Menu item '{menu_item.name}' created by {user_role} {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Menu item created successfully',
            'data': menu_item.to_dict(),
            'created_by': {'role': user_role}
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Database integrity error',
            'error': str(e.orig)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error creating menu item',
            'error': str(e)
        }), 500


@menu_bp.route('/<string:menu_id>', methods=['PUT'])
@permission_required('menu.update')
def update_menu_item(menu_id):
    """Update menu item - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        try:
            uuid.UUID(menu_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid menu item ID format'
            }), 400
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM menu_items WHERE id = %s", (menu_id,))
            if not cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'Menu item not found'
                }), 404
            
            update_fields = []
            update_values = []
            
            if 'is_available' in data:
                update_fields.append("is_available = %s")
                update_values.append(bool(data['is_available']))
            if 'name' in data:
                update_fields.append("name = %s")
                update_values.append(data['name'])
            if 'description' in data:
                update_fields.append("description = %s")
                update_values.append(data['description'])
            if 'image_url' in data:
                update_fields.append("image_url = %s")
                update_values.append(data['image_url'])
            if 'price' in data:
                update_fields.append("price = %s")
                update_values.append(float(data['price']))
            if 'category' in data:
                update_fields.append("category = %s")
                update_values.append(data['category'])
            if 'preparation_time' in data:
                update_fields.append("preparation_time = %s")
                update_values.append(int(data['preparation_time']))
            if 'allergens' in data:
                update_fields.append("allergens = %s")
                update_values.append(json.dumps(data['allergens']) if data['allergens'] is not None else None)
            if 'nutritional_info' in data:
                update_fields.append("nutritional_info = %s")
                update_values.append(json.dumps(data['nutritional_info']) if data['nutritional_info'] is not None else None)
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_query = f"UPDATE menu_items SET {', '.join(update_fields)} WHERE id = %s"
                update_values.append(menu_id)
                
                cursor.execute(update_query, update_values)
                conn.commit()
            
            cursor.execute("SELECT * FROM menu_items WHERE id = %s", (menu_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                row_dict = dict(zip(columns, result))
                
                updated_item = {
                    'id': row_dict['id'],
                    'name': row_dict['name'],
                    'description': row_dict['description'],
                    'image_url': row_dict['image_url'],
                    'price': float(row_dict['price']) if row_dict['price'] else 0,
                    'category': row_dict['category'],
                    'is_available': row_dict['is_available'],
                    'preparation_time': row_dict['preparation_time'],
                    'allergens': json.loads(row_dict['allergens']) if row_dict['allergens'] else [],
                    'nutritional_info': json.loads(row_dict['nutritional_info']) if row_dict['nutritional_info'] else {},
                    'created_at': row_dict['created_at'].isoformat() if row_dict['created_at'] else None,
                    'updated_at': row_dict['updated_at'].isoformat() if row_dict['updated_at'] else None
                }
                
                print(f"[AUDIT] Menu item {menu_id} updated by {user_role}")
                
                return jsonify({
                    'success': True,
                    'message': 'Menu item updated successfully',
                    'data': updated_item,
                    'updated_by_role': user_role
                })
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating menu item',
            'error': str(e)
        }), 500


@menu_bp.route('/<string:menu_id>', methods=['DELETE'])
@role_required('manager')
def delete_menu_item(menu_id):
    """Delete menu item - PROTECTED: Manager only"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        
        try:
            uuid.UUID(menu_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid menu item ID format'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, name FROM menu_items WHERE id = %s", (menu_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({
                    'success': False,
                    'message': 'Menu item not found'
                }), 404

            #fetch all order items associated with this menu item
            cursor.execute("SELECT id FROM order_items WHERE menu_item_id = %s", (menu_id,))
            order_items = cursor.fetchall()
            order_item_ids = [item[0] for item in order_items]
            if order_item_ids:
                #delete associated order items
                cursor.execute("DELETE FROM order_items WHERE menu_item_id = %s", (menu_id,))
                print(f"[AUDIT] Deleted associated order items {order_item_ids} for menu item {menu_id}")
            
            item_name = result[1]
            cursor.execute("DELETE FROM menu_items WHERE id = %s", (menu_id,))
            conn.commit()
            
            print(f"[AUDIT] Menu item '{item_name}' ({menu_id}) deleted by manager {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Menu item deleted successfully'
            })
            
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error deleting menu item',
            'error': str(e)
        }), 500
