from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from flasgger import swag_from
from docs.auth_docs import login_spec, register_spec, get_roles_spec
from models import db, User
from auth import ROLES
from datetime import datetime, timezone

from auth import (
    role_required,
    permission_required,
    authentication_required
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@swag_from(login_spec)
def login():
    """User login with role-based authentication"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password required'
            }), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is disabled'
            }), 403
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create tokens with role in claims
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'username': user.username,
                'email': user.email
            }
        )
        
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login error',
            'error': str(e)
        }), 500


@auth_bp.route('/register', methods=['POST'])
@role_required('manager')
@swag_from(register_spec)
def register():
    """Register new user - Only managers can create users"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate role
        valid_roles = ['manager', 'chef', 'waiter', 'cashier']
        if data['role'] not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            full_name=data['full_name']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration error',
            'error': str(e)
        }), 500

@auth_bp.route('/roles', methods=['GET'])
@authentication_required()
@swag_from(get_roles_spec)
def get_roles():
    """Get available roles and their permissions"""
    claims = get_jwt()
    current_role = claims.get('role')
    
    return jsonify({
        'success': True,
        'your_role': current_role,
        'available_roles': ROLES
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'User not found or inactive'
            }), 404
        
        # Create new access token with updated claims
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'username': user.username,
                'email': user.email
            }
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Token refresh error',
            'error': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@authentication_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200
