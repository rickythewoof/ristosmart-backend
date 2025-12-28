"""
Swagger/OpenAPI documentation for User and Check-in endpoints
"""

get_all_users_spec = {
    "tags": ["Users"],
    "summary": "Get all users",
    "description": "Retrieve all users (Manager only)",
    "security": [{"Bearer": []}],
    "responses": {
        200: {
            "description": "Users retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "format": "uuid"},
                                "username": {"type": "string", "example": "john_waiter"},
                                "email": {"type": "string", "example": "john@test.com"},
                                "full_name": {"type": "string", "example": "John Doe"},
                                "role": {"type": "string", "example": "waiter"},
                                "is_active": {"type": "boolean", "example": True},
                                "created_at": {"type": "string", "format": "date-time"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "count": {"type": "integer", "example": 10}
                }
            }
        }
    }
}

get_current_user_spec = {
    "tags": ["Users"],
    "summary": "Get current user",
    "description": "Get information about the currently authenticated user",
    "security": [{"Bearer": []}],
    "responses": {
        200: {
            "description": "User info retrieved",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "username": {"type": "string", "example": "john_waiter"},
                            "email": {"type": "string", "example": "john@test.com"},
                            "full_name": {"type": "string", "example": "John Doe"},
                            "role": {"type": "string", "example": "waiter"},
                            "is_active": {"type": "boolean", "example": True},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    }
}

get_user_by_id_spec = {
    "tags": ["Users"],
    "summary": "Get user by ID",
    "description": "Retrieve a specific user by UUID (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "User retrieved",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "username": {"type": "string", "example": "john_waiter"},
                            "email": {"type": "string", "example": "john@test.com"},
                            "full_name": {"type": "string", "example": "John Doe"},
                            "role": {"type": "string", "example": "waiter"},
                            "is_active": {"type": "boolean", "example": True},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        },
        404: {"description": "User not found"}
    }
}

update_user_spec = {
    "tags": ["Users"],
    "summary": "Update user",
    "description": "Update user information (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "full_name": {"type": "string"},
                    "role": {"type": "string", "enum": ["manager", "waiter", "chef", "cashier"]},
                    "is_active": {"type": "boolean"}
                },
                "example": {
                    "full_name": "John Updated Doe",
                    "is_active": True
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "User updated",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        }
    }
}

delete_user_spec = {
    "tags": ["Users"],
    "summary": "Delete user",
    "description": "Delete a user account (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "User deleted",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"}
                }
            }
        }
    }
}

# Check-in endpoints

get_user_checkins_spec = {
    "tags": ["Users"],
    "summary": "Get user check-ins",
    "description": "Get all check-ins for a specific user",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Check-ins retrieved",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "format": "uuid"},
                                "user_id": {"type": "string", "format": "uuid"},
                                "check_in_time": {"type": "string", "format": "date-time"},
                                "check_out_time": {"type": "string", "format": "date-time"},
                                "created_at": {"type": "string", "format": "date-time"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "count": {"type": "integer", "example": 25}
                }
            }
        }
    }
}

create_checkin_spec = {
    "tags": ["Users"],
    "summary": "Create check-in",
    "description": "Create a new check-in for user (clock-in)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        201: {
            "description": "Check-in created",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "User already checked in"}
    }
}

get_current_checkin_spec = {
    "tags": ["Users"],
    "summary": "Get current check-in",
    "description": "Get active check-in for user (if any)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Active check-in found",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "user_id": {"type": "string", "format": "uuid"},
                            "check_in_time": {"type": "string", "format": "date-time"},
                            "check_out_time": {"type": "string", "format": "date-time"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        },
        404: {"description": "No active check-in"}
    }
}

update_checkin_spec = {
    "tags": ["Users"],
    "summary": "Update check-in (check-out)",
    "description": "Update check-in with check-out time (clock-out)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        },
        {
            "name": "checkin_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Check-out successful",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        }
    }
}

delete_checkin_spec = {
    "tags": ["Users"],
    "summary": "Delete check-in",
    "description": "Delete a check-in record (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        },
        {
            "name": "checkin_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Check-in deleted",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"}
                }
            }
        },
        404: {"description": "Check-in not found"}
    }
}
