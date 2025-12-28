from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid
import json
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Timezone italiana
ITALY_TZ = pytz.timezone('Europe/Rome')

def italy_now():
    """Restituisce l'ora corrente nel fuso orario italiano"""
    return datetime.now(ITALY_TZ).replace(tzinfo=None)


# ============ USER MODEL (Authentication) ============

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='waiter')
    full_name = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

# ============ CHECK-IN MODEL ============
class CheckIn(db.Model):
    __tablename__ = 'check_ins'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    check_out_time = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref=db.backref('check_ins', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None
        }

# ============ MENU MODEL ============

class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(20), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    preparation_time = db.Column(db.Integer, nullable=False)
    allergens = db.Column(db.Text)  # Stored as JSON string
    nutritional_info = db.Column(db.Text)  # Stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'category': self.category,
            'is_available': self.is_available,
            'preparation_time': self.preparation_time,
            'allergens': json.loads(self.allergens) if self.allergens else [],
            'nutritional_info': json.loads(self.nutritional_info) if self.nutritional_info else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============ ORDER MODELS ============

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    table_number = db.Column(db.Integer)
    customer_name = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'payed', 'cancelled', name='order_status'), 
                      default='pending', nullable=False)
    order_type = db.Column(db.Enum('dine_in', 'takeout', 'delivery', name='order_type'), default='dine_in', nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    final_amount = db.Column(db.Numeric(10, 2), default=0)
    special_instructions = db.Column(db.Text)
    estimated_completion_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=italy_now)
    updated_at = db.Column(db.DateTime, default=italy_now, onupdate=italy_now)
    
    # Relationship with order items
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id),
            'order_number': self.order_number,
            'table_number': self.table_number,
            'customer_name': self.customer_name,
            'status': self.status,
            'order_type': self.order_type,
            'total_amount': float(self.total_amount),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'final_amount': float(self.final_amount),
            'special_instructions': self.special_instructions,
            'estimated_completion_time': self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.String(36), db.ForeignKey('menu_items.id', ondelete='CASCADE'), nullable=False)
    menu_item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    special_instructions = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'preparing', 'ready', 'served', 'cancelled', name='order_item_status'), 
                      default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=italy_now)
    updated_at = db.Column(db.DateTime, default=italy_now, onupdate=italy_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'menu_item_id': str(self.menu_item_id),
            'menu_item_name': self.menu_item_name,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'special_instructions': self.special_instructions,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============ PRODUCT MODEL ============
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ean = db.Column(db.String(13), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=italy_now)
    updated_at = db.Column(db.DateTime, default=italy_now, onupdate=italy_now)

    def to_dict(self):
        return {
            'id': str(self.id),
            'ean': self.ean,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
