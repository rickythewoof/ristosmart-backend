from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from auth import permission_required
from models import db, Product, italy_now
from marshmallow import Schema, fields, ValidationError
import uuid

from flasgger import swag_from

from docs.inventory_docs import (
    get_all_products_spec,
    get_product_spec,
    create_product_spec,
    update_product_spec,
    delete_product_spec
)

inventory_bp = Blueprint('inventory', __name__)

class ProductSchema(Schema):
    id = fields.Str(dump_only=True)
    ean = fields.Str(required=True, validate=lambda x: len(x) in [8, 13])  # EAN-8 or EAN-13
    name = fields.Str(required=True, validate=lambda x: 1 <= len(x) <= 100)
    description = fields.Str(allow_none=True)
    price = fields.Float(required=True, validate=lambda x: x >= 0)
    category = fields.Str(allow_none=True, validate=lambda x: len(x) <= 50)
    image_url = fields.Str(allow_none=True, validate=lambda x: len(x) <= 255)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
@swag_from(get_all_products_spec)
def get_products():
    """Get all products"""
    try:
        products = Product.query.all()
        return jsonify({
            'success': True,
            'data': products_schema.dump(products),
            'count': len(products)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching products',
            'error': str(e)
        }), 500

@inventory_bp.route('/<product_id>', methods=['GET'])
@jwt_required()
@swag_from(get_product_spec)
def get_product(product_id):
    """Get single product by ID"""
    try:
        # Validate UUID
        try:
            uuid.UUID(product_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid product ID format'
            }), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product_schema.dump(product)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching product',
            'error': str(e)
        }), 500

@inventory_bp.route('/', methods=['POST'])
@permission_required('add_product')
@swag_from(create_product_spec)
def add_product():
    """Add new product"""
    try:
        # Validate input with schema
        try:
            data = product_schema.load(request.get_json())
        except ValidationError as ve:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': ve.messages
            }), 400
        
        # Check if EAN already exists
        existing = Product.query.filter_by(ean=data['ean']).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Product with this EAN already exists'
            }), 409
        
        # Create new product
        new_product = Product(
            ean=data['ean'],
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            category=data.get('category'),
            image_url=data.get('image_url')
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product added successfully',
            'data': product_schema.dump(new_product)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error adding product',
            'error': str(e)
        }), 500

@inventory_bp.route('/<product_id>', methods=['PUT'])
@swag_from(update_product_spec)
@permission_required('edit_product')
def update_product(product_id):
    """Update existing product"""
    try:
        # Validate UUID
        try:
            uuid.UUID(product_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid product ID format'
            }), 400
        
        # Find product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Validate input with schema
        try:
            data = product_schema.load(request.get_json(), partial=True)
        except ValidationError as ve:
            return jsonify({
                'success': False,
                'message': 'Validation error',
                'errors': ve.messages
            }), 400
        
        # Check if EAN is being changed and if it already exists
        if 'ean' in data and data['ean'] != product.ean:
            existing = Product.query.filter_by(ean=data['ean']).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Product with this EAN already exists'
                }), 409
        
        # Update fields
        for key, value in data.items():
            setattr(product, key, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully',
            'data': product_schema.dump(product)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error updating product',
            'error': str(e)
        }), 500

@inventory_bp.route('/<product_id>', methods=['DELETE'])
@swag_from(delete_product_spec)
@permission_required('delete_product')
def delete_product(product_id):
    """Delete product"""
    try:
        # Validate UUID
        try:
            uuid.UUID(product_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid product ID format'
            }), 400
        
        # Find product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        product_name = product.name
        
        # Delete product
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Product "{product_name}" deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting product',
            'error': str(e)
        }), 500