import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_NAME = os.getenv('DB_NAME', 'ristosmart')

    MANAGER_USER = os.getenv('MANAGER_USER', 'manager@ristosmart.it')
    MANAGER_PASSWORD = os.getenv('MANAGER_PASSWORD', 'changemeplease!')

    # Database URI configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Check if running on Cloud Run (Cloud SQL Unix socket)
    INSTANCE_UNIX_SOCKET = os.getenv('INSTANCE_UNIX_SOCKET')
    
    if INSTANCE_UNIX_SOCKET:
        # Cloud Run with Cloud SQL Unix Socket (più affidabile)
        # Formato corretto per Cloud SQL Proxy Unix Socket
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?unix_sock={INSTANCE_UNIX_SOCKET}/.s.PGSQL.5432"
    elif DATABASE_URL:
        # Fix for some cloud providers that use postgres:// instead of postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Get SSL mode from environment
    DB_SSLMODE = os.getenv('DB_SSLMODE', 'disable')
    
    # Connection pool configuration optimized for Cloud Run
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # Test connections before using
        'pool_recycle': 300,         # Match Cloud SQL timeout
        'pool_size': 5,              # Small pool for serverless
        'max_overflow': 2,           # Limited overflow
        'pool_timeout': 30,
        'isolation_level': 'READ COMMITTED',  # Prevent transaction issues
    }
    
    # Add SSL/TCP configs only if NOT using Unix socket and NOT localhost
    if not INSTANCE_UNIX_SOCKET and DB_HOST not in ['localhost', '127.0.0.1', 'db']:
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'sslmode': DB_SSLMODE,
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
            'options': '-c statement_timeout=30000'  # 30s statement timeout
        }

    PORT = int(os.environ.get('PORT', 3000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

    BASE_URL = os.getenv('BASE_URL', f'http://localhost:{PORT}')
    SWAGGER_HOST = BASE_URL.replace('https://', '').replace('http://', '').rstrip('/')

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ALGORITHM = 'HS256'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}