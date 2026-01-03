from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from datetime import datetime, timezone
import time
import uuid
import sys
import os

from config import config
from models import db
from swagger_config import swagger_template, swagger_config

from models import User

def wait_for_db(app, max_retries=10, delay=2):
    """Wait for database to be ready before proceeding"""
    print("Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to connect to the database
                db.engine.connect()
                print(f"Database connection successful!")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"{e} Database not ready yet (attempt {attempt + 1}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                return False
    
    return False

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
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default manager: {e}")


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    jwt = JWTManager(app)
    
    # Initialize Swagger
    Swagger(app, template=swagger_template, config=swagger_config)
    
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
    from routes.inventory import inventory_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'service': 'RistoSmart API',
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
                },
                'inventory': {
                    'GET /api/inventory/': 'Get all products',
                    'GET /api/inventory/{id}': 'Get product by ID',
                    'POST /api/inventory/': 'Create new product',
                    'PUT /api/inventory/{id}': 'Update product',
                    'DELETE /api/inventory/{id}': 'Delete product'
                }
            }
        })
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'ristosmart-backend',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime': time.process_time()
        })
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            if exception:
                db.session.rollback()
        except Exception as e:
            app.logger.error(f"Error during session rollback: {e}")
        finally:
            try:
                db.session.remove()
            except Exception as e:
                app.logger.error(f"Error during session removal: {e}")
    
    # Error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Rollback on any unhandled exception
        try:
            db.session.rollback()
        except:
            pass
        
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(type(e).__name__)
        }), 500
    
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
    
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')

    # Create tables
    with app.app_context():
        if not wait_for_db(app):
            print("ERROR: Could not establish database connection. Exiting...")
            sys.exit(1)
        
        db.create_all()
        print("Database tables created successfully")
        
        create_default_manager(app)
        
    
    return app


app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = app.config.get('PORT', 3000)
    print(f"Ristosmart Unified Backend starting on port {port}")
    print(f"API Documentation available at http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)
