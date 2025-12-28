from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from flasgger import swag_from
from docs.user_docs import (
    get_all_users_spec,
    get_current_user_spec,
    get_user_by_id_spec,
    update_user_spec,
    delete_user_spec,
    get_user_checkins_spec,
    create_checkin_spec,
    get_current_checkin_spec,
    update_checkin_spec,
    delete_checkin_spec
)
from models import db, CheckIn, User
from datetime import datetime, timezone
from auth import role_required, authentication_required


user_bp = Blueprint('users', __name__)

# ========== USER COLLECTION ==========

@user_bp.route('/', methods=['GET'])
@role_required('manager')
@swag_from(get_all_users_spec)
def get_users():
    """Get list of all users (Collection)"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching users',
            'error': str(e)
        }), 500


@user_bp.route('/', methods=['POST'])
@role_required('manager')
def create_user():
    """Create a new user (POST to collection)"""
    try:
        data = request.get_json()
        # Implementation here
        return jsonify({
            'success': True,
            'data': new_user.to_dict()
        }), 201  # 201 Created
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error creating user',
            'error': str(e)
        }), 500


# ========== INDIVIDUAL USER RESOURCE ==========

@user_bp.route('/me', methods=['GET'])
@authentication_required()
@swag_from(get_current_user_spec)
def get_current_user():
    """Get current authenticated user (special case)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching user info',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['GET'])
@role_required('manager')
@swag_from(get_user_by_id_spec)
def get_user(user_id):
    """Get specific user by ID"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching user',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['PUT'])
@role_required('manager')
@swag_from(update_user_spec)
def update_user(user_id):
    """Update user (full update)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        # Update user fields
        # user.email = data.get('email', user.email)
        # etc.
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating user',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['PATCH'])
@role_required('manager')
def partial_update_user(user_id):
    """Partially update user (only provided fields)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        # Only update provided fields
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error updating user',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>', methods=['DELETE'])
@role_required('manager')
@swag_from(delete_user_spec)
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200  # or 204 No Content
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error deleting user',
            'error': str(e)
        }), 500


# ========== CHECK-IN SUB-RESOURCE ==========

@user_bp.route('/<user_id>/checkins', methods=['GET'])
@authentication_required()
@swag_from(get_user_checkins_spec)
def get_user_checkins(user_id):
    """Get all check-ins for a user"""
    try:
        current_user = get_jwt_identity()
        if current_user != user_id and current_user.get('role') != 'manager':
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403
        
        checkins = CheckIn.query.filter_by(user_id=user_id).order_by(CheckIn.check_in_time.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [checkin.to_dict() for checkin in checkins]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching check-ins',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>/checkins', methods=['POST'])
@authentication_required()
@swag_from(create_checkin_spec)
def create_checkin(user_id):
    """Create a new check-in"""
    current_user = None
    try:
        current_user = get_jwt_identity()
        if current_user != user_id and current_user.get('role') != 'manager':
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403

        # Check for existing active check-in
        active_checkin = CheckIn.query.filter_by(
            user_id=user_id, 
            check_out_time=None
        ).first()
        
        if active_checkin:
            return jsonify({
                'success': False,
                'message': 'User already checked in'
            }), 400

        checkin = CheckIn(
            user_id=user_id,
            check_in_time=datetime.now(timezone.utc),
            check_out_time=None
        )

        db.session.add(checkin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': checkin.to_dict(),
            'message': 'Check-in successful'
        }), 201  # 201 Created
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error during check-in for user {user_id}',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>/checkins/current', methods=['GET'])
@authentication_required()
@swag_from(get_current_checkin_spec)
def get_current_checkin(user_id):
    """Get currently active check-in"""
    try:
        current_user = get_jwt_identity()
        if current_user != user_id and current_user.get('role') != 'manager':
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403

        active_checkin = CheckIn.query.filter_by(
            user_id=user_id,
            check_out_time=None
        ).first()
        
        if not active_checkin:
            return jsonify({
                'success': False,
                'message': 'No active check-in found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': active_checkin.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching check-in',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>/checkins/<checkin_id>', methods=['GET'])
@authentication_required()
def get_checkin(user_id, checkin_id):
    """Get specific check-in by ID"""
    try:
        current_user = get_jwt_identity()
        if current_user != user_id and current_user.get('role') != 'manager':
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403

        checkin = CheckIn.query.filter_by(
            id=checkin_id,
            user_id=user_id
        ).first()
        
        if not checkin:
            return jsonify({
                'success': False,
                'message': 'Check-in not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': checkin.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching check-in',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>/checkins/<checkin_id>', methods=['PUT'])
@authentication_required()
@swag_from(update_checkin_spec)
def update_checkin(user_id, checkin_id):
    """Update check-in (add checkout time """
    try:
        current_user = get_jwt_identity()
        if current_user != user_id and current_user.get('role') != 'manager':
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403

        checkin = CheckIn.query.filter_by(
            id=checkin_id,
            user_id=user_id
        ).first()
        
        if not checkin:
            return jsonify({
                'success': False,
                'message': 'Check-in not found'
            }), 404

        if checkin.check_out_time:
            return jsonify({
                'success': False,
                'message': 'Already checked out'
            }), 400

        data = request.get_json() or {}
        checkin.check_out_time = data.get('check_out_time') or datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': checkin.to_dict(),
            'message': 'Check-out successful'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error during check-out',
            'error': str(e)
        }), 500


@user_bp.route('/<user_id>/checkins/<checkin_id>', methods=['DELETE'])
@role_required('manager')
@swag_from(delete_checkin_spec)
def delete_checkin(user_id, checkin_id):
    """Delete check-in (manager only)"""
    try:
        checkin = CheckIn.query.filter_by(
            id=checkin_id,
            user_id=user_id
        ).first()
        
        if not checkin:
            return jsonify({
                'success': False,
                'message': 'Check-in not found'
            }), 404
        
        db.session.delete(checkin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Check-in deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error deleting check-in',
            'error': str(e)
        }), 500