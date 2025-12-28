"""
Swagger/OpenAPI Configuration for RistoSmart API
Complete API documentation with examples for all endpoints
"""

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "RistoSmart API",
        "description": "Complete REST API documentation for RistoSmart restaurant management system. "
                      "This API provides endpoints for managing menu items, orders, users, inventory, and check-ins.",
        "version": "1.0.0",
    },
    "host": "localhost:3000",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
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
