from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

ROLES = {
    'manager': {
        'permissions': ['*'],
        'description': 'Full access to all operations'
    },
    'chef': {
        'permissions': ['menu.read', 'menu.create', 'menu.update', 'order.read', 'order.update_status'],
        'description': 'Manage menu and order preparation'
    },
    'waiter': {
        'permissions': ['menu.read', 'order.read', 'order.create', 'order.update'],
        'description': 'Take orders and serve customers'
    },
    'cashier': {
        'permissions': ['menu.read', 'order.read', 'order.update_payment'],
        'description': 'Handle payments'
    }
}

def permission_required(permission):
    """
    Decorator to check if user has the required permission.
    Usage: @permission_required('menu.create')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if not user_role:
                return jsonify({
                    'success': False,
                    'message': 'No role found in token'
                }), 403
            
            # Manager has all permissions
            if user_role == 'manager':
                return fn(*args, **kwargs)
            
            # Check if role exists and has permission
            role_config = ROLES.get(user_role)
            if not role_config:
                return jsonify({
                    'success': False,
                    'message': f'Invalid role: {user_role}'
                }), 403
            
            if permission not in role_config['permissions']:
                return jsonify({
                    'success': False,
                    'message': f'Insufficient permissions. Required: {permission}',
                    'current_role': user_role,
                    'current_permissions': role_config['permissions']
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator



def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the allowed roles.
    Usage: @role_required('manager', 'chef')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if not user_role:
                return jsonify({
                    'success': False,
                    'message': 'No role found in token'
                }), 403
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}',
                    'your_role': user_role
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    claims = get_jwt()
    return claims.get('sub')

def get_current_user_role():
    claims = get_jwt()
    return claims.get('role')
