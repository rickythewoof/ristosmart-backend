"""
Swagger/OpenAPI documentation for Authentication endpoints
"""

login_spec = {
    "tags": ["Authentication"],
    "summary": "User login",
    "description": "Authenticate user and receive JWT access token",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["username", "password"],
                "properties": {
                    "username": {
                        "type": "string",
                        "example": "manager"
                    },
                    "password": {
                        "type": "string",
                        "format": "password",
                        "example": "manager123"
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Login successful",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "access_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGc..."},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "username": {"type": "string"},
                            "email": {"type": "string"},
                            "role": {"type": "string"}
                        }
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string"}
                }
            }
        }
    }
}

register_spec = {
    "tags": ["Authentication"],
    "summary": "Register new user",
    "description": "Create a new user account (manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["username", "email", "password", "full_name", "role"],
                "properties": {
                    "username": {"type": "string", "example": "john_waiter"},
                    "email": {"type": "string", "format": "email", "example": "john@test.com"},
                    "password": {"type": "string", "format": "password", "example": "SecurePass123!"},
                    "full_name": {"type": "string", "example": "John Doe"},
                    "role": {"type": "string", "enum": ["manager", "waiter", "chef", "cashier"], "example": "waiter"}
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "User created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "user": {"type": "object"}
                }
            }
        },
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Manager role required"}
    }
}

get_roles_spec = {
    "tags": ["Authentication"],
    "summary": "Get available roles",
    "description": "Retrieve list of all available user roles in the system",
    "security": [{"Bearer": []}],
    "responses": {
        200: {
            "description": "Roles retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "roles": {
                        "type": "object",
                        "example": {
                            "manager": {"permissions": ["all"]},
                            "chef": {"permissions": ["menu.create", "menu.update"]},
                            "waiter": {"permissions": ["order.create"]},
                            "cashier": {"permissions": ["order.update_payment"]}
                        }
                    }
                }
            }
        }
    }
}
