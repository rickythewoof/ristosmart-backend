"""
Swagger/OpenAPI documentation for Menu endpoints
"""

get_all_menu_items_spec = {
    "tags": ["Menu"],
    "summary": "Get all menu items",
    "description": "Retrieve all menu items with optional filtering (PUBLIC endpoint - no authentication required)",
    "parameters": [
        {
            "name": "category",
            "in": "query",
            "type": "string",
            "enum": ["appetizer", "main", "dessert", "beverage", "side"],
            "description": "Filter by category"
        },
        {
            "name": "available",
            "in": "query",
            "type": "string",
            "enum": ["true", "false"],
            "description": "Filter by availability"
        }
    ],
    "responses": {
        200: {
            "description": "Menu items retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "price": {"type": "number"},
                                "category": {"type": "string"},
                                "is_available": {"type": "boolean"},
                                "preparation_time": {"type": "integer"},
                                "allergens": {"type": "array", "items": {"type": "string"}},
                                "nutritional_info": {"type": "object"}
                            }
                        }
                    },
                    "count": {"type": "integer", "example": 15}
                }
            }
        }
    }
}

get_available_menu_items_spec = {
    "tags": ["Menu"],
    "summary": "Get available menu items",
    "description": "Retrieve only available menu items for ordering (PUBLIC endpoint)",
    "responses": {
        200: {
            "description": "Available menu items retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"type": "array"},
                    "count": {"type": "integer"}
                }
            }
        }
    }
}

get_menu_item_spec = {
    "tags": ["Menu"],
    "summary": "Get menu item by ID",
    "description": "Retrieve a specific menu item by its UUID (PUBLIC endpoint)",
    "parameters": [
        {
            "name": "menu_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Menu item UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Menu item retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Menu item not found"}
    }
}

create_menu_item_spec = {
    "tags": ["Menu"],
    "summary": "Create menu item",
    "description": "Create a new menu item (Chef or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "price", "category", "preparation_time"],
                "properties": {
                    "name": {"type": "string", "example": "Margherita Pizza"},
                    "description": {"type": "string", "example": "Classic Italian pizza with tomato and mozzarella"},
                    "image_url": {"type": "string", "example": "https://example.com/pizza.jpg"},
                    "price": {"type": "number", "example": 12.50},
                    "tax_amount": {"type": "number", "example": 0.1},
                    "category": {"type": "string", "enum": ["appetizer", "main", "dessert", "beverage", "side"], "example": "main"},
                    "is_available": {"type": "boolean", "example": True},
                    "preparation_time": {"type": "integer", "example": 15},
                    "allergens": {"type": "array", "items": {"type": "string"}, "example": ["gluten", "dairy"]},
                    "nutritional_info": {"type": "object", "example": {"calories": 850, "protein": 35, "carbs": 100}}
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "Menu item created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Chef or Manager role required"}
    }
}

update_menu_item_spec = {
    "tags": ["Menu"],
    "summary": "Update menu item",
    "description": "Update an existing menu item (Chef or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "menu_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Menu item UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "price": {"type": "number"},
                    "category": {"type": "string"},
                    "is_available": {"type": "boolean"},
                    "preparation_time": {"type": "integer"},
                    "allergens": {"type": "array"},
                    "nutritional_info": {"type": "object"}
                },
                "example": {
                    "price": 13.50,
                    "is_available": False
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Menu item updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Validation error"},
        404: {"description": "Menu item not found"}
    }
}

delete_menu_item_spec = {
    "tags": ["Menu"],
    "summary": "Delete menu item",
    "description": "Delete a menu item and all associated order items via CASCADE (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "menu_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Menu item UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Menu item deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"}
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Menu item not found"},
        403: {"description": "Forbidden - Manager role required"}
    }
}
