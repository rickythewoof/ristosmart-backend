"""
Swagger/OpenAPI Configuration for RistoSmart API
Complete API documentation with examples for all endpoints
"""
import os

# Get SWAGGER_HOST from environment or config
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
SWAGGER_HOST = BASE_URL.replace('https://', '').replace('http://', '').rstrip('/')
SWAGGER_SCHEME = 'https' if 'https://' in BASE_URL else 'http'

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "RistoSmart API",
        "description": "Complete REST API documentation for RistoSmart restaurant management system. "
                      "This API provides endpoints for managing menu items, orders, users, inventory, and check-ins.",
        "version": "1.0.0",
    },
    "host": SWAGGER_HOST,
    "basePath": "/api",
    "schemes": [SWAGGER_SCHEME, "http"] if SWAGGER_SCHEME == "https" else ["http"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Enter: Bearer YOUR_TOKEN_HERE"
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User authentication and registration endpoints"
        },
        {
            "name": "Menu",
            "description": "Menu item management (public and protected endpoints)"
        },
        {
            "name": "Orders",
            "description": "Order creation and management"
        },
        {
            "name": "Users",
            "description": "User management and check-in/check-out system"
        },
        {
            "name": "Inventory",
            "description": "Product inventory management"
        }
    ]
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}
