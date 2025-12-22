import os
from datetime import timedelta

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_NAME = os.getenv('DB_NAME', 'ristosmart')

    MANAGER_USER = os.getenv('MANAGER_USER', 'manager@ristosmart.it')
    MANAGER_PASSWORD = os.getenv('MANAGER_PASSWORD', 'changemeplease!')

    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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

    if not os.getenv('JWT_SECRET_KEY') or JWT_SECRET_KEY == 'super-secret-jwt-key-change-in-production':   # type: ignore
        raise ValueError("Please set a strong JWT_SECRET_KEY environment variable for production")
    
    if not os.getenv('SECRET_KEY') or SECRET_KEY == 'default_secret_key':   # type: ignore
        raise ValueError("Please set a strong SECRET_KEY environment variable for production")
    
    if not os.getenv('MANAGER_PASSWORD') or MANAGER_PASSWORD == 'changemeplease!':   # type: ignore
        raise ValueError("Please set a strong MANAGER_PASSWORD environment variable for production")
    
    if not os.getenv('DB_PASSWORD') or DB_PASSWORD == 'password':   # type: ignore
        raise ValueError("Please set a strong DB_PASSWORD environment variable for production")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

}