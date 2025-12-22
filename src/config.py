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

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    PORT = int(os.environ.get('PORT', 3000))
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

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

    if not os.getenv('JWT_SECRET_KEY') or Config.JWT_SECRET_KEY == 'super-secret-jwt-key-change-in-production':   # type: ignore
        raise ValueError("Please set a strong JWT_SECRET_KEY environment variable for production")
    
    if not os.getenv('SECRET_KEY') or Config.SECRET_KEY == 'default_secret_key':   # type: ignore
        raise ValueError("Please set a strong SECRET_KEY environment variable for production")

    if not os.getenv('MANAGER_PASSWORD') or Config.MANAGER_PASSWORD == 'changemeplease!':   # type: ignore
        raise ValueError("Please set a strong MANAGER_PASSWORD environment variable for production")

    if not os.getenv('DB_PASSWORD') or Config.DB_PASSWORD == 'password':   # type: ignore
        raise ValueError("Please set a strong DB_PASSWORD environment variable for production")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig

}