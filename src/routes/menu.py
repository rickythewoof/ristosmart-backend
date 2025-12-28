from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from models import db, MenuItem, OrderItem
from auth import permission_required, role_required
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError
import uuid
import json

from flasgger import swag_from
from docs.menu_docs import (
    get_all_menu_items_spec,
    get_available_menu_items_spec,
    get_menu_item_spec,
    create_menu_item_spec,
    update_menu_item_spec,
    delete_menu_item_spec
)

menu_bp = Blueprint('menu', __name__)

# Marshmallow schemas for validation
class MenuItemSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 100)
    description = fields.Str(allow_none=True)
    image_url = fields.Str(allow_none=True)
    price = fields.Float(required=True, validate=lambda x: x >= 0)
    tax_amount = fields.Float(allow_none=True, validate=lambda x: x >= 0 and x <= 1)
    category = fields.Str(required=True, validate=lambda x: x in ['appetizer', 'main', 'dessert', 'beverage', 'side'])
    is_available = fields.Bool(missing=True)
    preparation_time = fields.Int(required=True, validate=lambda x: x >= 1)
    allergens = fields.List(fields.Str(), allow_none=True)
    nutritional_info = fields.Dict(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)


# ============ PUBLIC ENDPOINTS ============

@swag_from(get_all_menu_items_spec)
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
        
        # Convert to dict first to deserialize JSON fields (allergens, nutritional_info)
        menu_items_data = [item.to_dict() for item in menu_items]
        
        return jsonify({
            'success': True,
            'data': menu_items_data,
            'count': len(menu_items)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching menu items',
            'error': str(e)
        }), 500


@menu_bp.route('/available', methods=['GET'])
@swag_from(get_available_menu_items_spec)
def get_available_menu_items():
    """Get available menu items for ordering - PUBLIC"""
    try:
        menu_items = MenuItem.query.filter(MenuItem.is_available == True).all()
        
        # Convert to dict first to deserialize JSON fields
        menu_items_data = [item.to_dict() for item in menu_items]
        
        return jsonify({
            'success': True,
            'data': menu_items_data,
            'count': len(menu_items)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching available menu items',
            'error': str(e)
        }), 500


@menu_bp.route('/<string:menu_id>', methods=['GET'])
@swag_from(get_menu_item_spec)
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
        
        menu_item = MenuItem.query.get(menu_id)
        
        if not menu_item:
            return jsonify({
                'success': False,
                'message': 'Menu item not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': menu_item.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching menu item',
            'error': str(e)
        }), 500


# ============ PROTECTED ENDPOINTS ============

@menu_bp.route('/', methods=['POST'])
@permission_required('menu.create')
@swag_from(create_menu_item_spec)
def create_menu_item():
    """Create a new menu item - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        print(f"[AUDIT] Menu item creation attempt by user {user_id} ({user_role})")
        
        # Validate input with schema
        try:
            data = menu_item_schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        # Create menu item using ORM
        menu_item = MenuItem(
            name=data['name'],
            description=data.get('description'),
            image_url=data.get('image_url'),
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
@swag_from(update_menu_item_spec)
def update_menu_item(menu_id):
    """Update menu item - PROTECTED: Chef, Manager"""
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        user_role = claims.get('role')
        
        try:
            uuid.UUID(menu_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid menu item ID format'
            }), 400
        
        menu_item = MenuItem.query.get(menu_id)
        
        if not menu_item:
            return jsonify({
                'success': False,
                'message': 'Menu item not found'
            }), 404
        
        try:
            data = menu_item_schema.load(request.json, partial=True)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': err.messages
            }), 400
        
        for key, value in data.items():
            if key in ['allergens', 'nutritional_info'] and value is not None:
                setattr(menu_item, key, json.dumps(value))
            else:
                setattr(menu_item, key, value)
        
        db.session.commit()
        
        print(f"[AUDIT] Menu item {menu_id} updated by {user_role} {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Menu item updated successfully',
            'data': menu_item.to_dict(),
            'updated_by_role': user_role
        }), 200
        
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
            'message': 'Error updating menu item',
            'error': str(e)
        }), 500


@menu_bp.route('/<string:menu_id>', methods=['DELETE'])
@role_required('manager')
@swag_from(delete_menu_item_spec)
def delete_menu_item(menu_id):
    """Delete menu item - PROTECTED: Manager only
    
    Note: Associated order_items will be automatically deleted via CASCADE constraint
    """
    try:
        claims = get_jwt()
        user_id = claims.get('sub')
        
        # Validate UUID
        try:
            uuid.UUID(menu_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid menu item ID format'
            }), 400
        
        # Find menu item using ORM
        menu_item = MenuItem.query.get(menu_id)
        
        if not menu_item:
            return jsonify({
                'success': False,
                'message': 'Menu item not found'
            }), 404
        
        item_name = menu_item.name
        
        # Check if there are associated order items (for logging purposes)
        associated_count = OrderItem.query.filter_by(menu_item_id=menu_id).count()
        if associated_count > 0:
            print(f"[AUDIT] Deleting menu item {menu_id} will CASCADE delete {associated_count} associated order items")
        
        # Delete menu item (CASCADE will automatically delete associated order_items)
        db.session.delete(menu_item)
        db.session.commit()
        
        print(f"[AUDIT] Menu item '{item_name}' ({menu_id}) deleted by manager {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Menu item deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting menu item',
            'error': str(e)
        }), 500
