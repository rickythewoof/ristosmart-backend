from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timezone
import time
import uuid

from config import config
from models import db

from models import User

def create_default_manager(app):
    """Create default manager user if it doesn't exist"""
    with app.app_context():
        manager_email = app.config.get('MANAGER_USER')
        manager_password = app.config.get('MANAGER_PASSWORD')
        
        if not manager_email or not manager_password:
            print("No manager credentials found in configuration")
            return
        
        # Check if manager already exists
        existing_manager = User.query.filter_by(email=manager_email).first()
        
        if existing_manager:
            print(f"Manager already exists: {manager_email}")
            return
        
        # Create default manager
        try:
            manager = User(
                id=str(uuid.uuid4()),
                email=manager_email,
                username=manager_email.split('@')[0],
                full_name="System Manager",
                role='manager',
                is_active=True
            )
            manager.set_password(manager_password)
            
            db.session.add(manager)
            db.session.commit()
            
            print(f"Default manager created successfully!")
            print(f"   Email: {manager.email}")
            print(f"   Username: {manager.username}")
            print(f"   Role: {manager.role}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default manager: {e}")


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authorization token required',
            'error': 'authorization_required'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has been revoked',
            'error': 'token_revoked'
        }), 401
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.orders import order_bp
    from routes.users import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'service': 'ByteRisto API',
            'version': '2.0.0',
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'endpoints': {
                'auth': {
                    'POST /api/auth/login': 'User login',
                    'POST /api/auth/register': 'Register new user (manager only)',
                    'GET /api/auth/roles': 'Get available roles',
                    'POST /api/auth/refresh': 'Refresh access token',
                    'POST /api/auth/logout': 'Logout'
                },
                'users': {
                    'GET /api/users': 'Get all users (manager only)',
                    'GET /api/users/me': 'Get current user info',
                    'GET /api/users/{id}': 'Get user by ID (manager only)',
                    'PUT /api/users/{id}': 'Update user (manager only)',
                    'PATCH /api/users/{id}': 'Partially update user (manager only)',
                    'DELETE /api/users/{id}': 'Delete user (manager only)'
                },
                'checkins': {
                    'GET /api/users/{id}/checkins': 'Get all check-ins for user',
                    'POST /api/users/{id}/checkins': 'Create new check-in',
                    'GET /api/users/{id}/checkins/current': 'Get active check-in',
                    'GET /api/users/{id}/checkins/{checkin_id}': 'Get specific check-in',
                    'PUT /api/users/{id}/checkins/{checkin_id}': 'Update check-in (checkout)',
                    'DELETE /api/users/{id}/checkins/{checkin_id}': 'Delete check-in (manager only)'
                },
                'menu': {
                    'GET /api/menu/': 'Get all menu items (public)',
                    'GET /api/menu/available': 'Get available menu items (public)',
                    'GET /api/menu/{id}': 'Get menu item by ID (public)',
                    'POST /api/menu/': 'Create menu item (chef, manager)',
                    'PUT /api/menu/{id}': 'Update menu item (chef, manager)',
                    'DELETE /api/menu/{id}': 'Delete menu item (manager only)'
                },
                'orders': {
                    'GET /api/orders/': 'Get all orders',
                    'GET /api/orders/{id}': 'Get order by ID',
                    'POST /api/orders/': 'Create new order (waiter, manager)',
                    'PUT /api/orders/{id}/status': 'Update order status (chef, manager)',
                    'PUT /api/orders/{id}/items/{item_id}/status': 'Update order item status (chef, manager)',
                    'POST /api/orders/{id}/pay': 'Process payment (cashier, manager)',
                    'DELETE /api/orders/{id}': 'Delete order'
                }
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'byteristo-unified-backend',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime': time.process_time()
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error': 'not_found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'internal_error'
        }), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        
        # Check if default manager exists, if not create one
        create_default_manager(app)
    
    return app


if __name__ == '__main__':
    import os
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    port = app.config.get('PORT', 3000)
    print(f"Ristosmart Unified Backend starting on port {port}")
    print(f"📚 API Documentation available at http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)
