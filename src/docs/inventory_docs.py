"""
Swagger/OpenAPI documentation for Inventory endpoints
"""

get_all_products_spec = {
    "tags": ["Inventory"],
    "summary": "Get all products",
    "description": "Retrieve all products in inventory",
    "security": [{"Bearer": []}],
    "responses": {
        200: {
            "description": "Products retrieved successfully",
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
                                "ean": {"type": "string", "example": "1234567890123"},
                                "name": {"type": "string", "example": "Coca Cola 330ml"},
                                "description": {"type": "string"},
                                "price": {"type": "number", "example": 2.50},
                                "category": {"type": "string", "example": "beverages"},
                                "image_url": {"type": "string"},
                                "created_at": {"type": "string", "format": "date-time"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "count": {"type": "integer", "example": 50}
                }
            }
        },
        401: {"description": "Unauthorized"}
    }
}


get_product_spec = {
    "tags": ["Inventory"],
    "summary": "Get product by ID",
    "description": "Retrieve a specific product by UUID",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Product UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Product retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "ean": {"type": "string", "example": "1234567890123"},
                            "name": {"type": "string", "example": "Coca Cola 330ml"},
                            "description": {"type": "string"},
                            "price": {"type": "number", "example": 2.50},
                            "category": {"type": "string", "example": "beverages"},
                            "image_url": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Product not found"}
    }
}

create_product_spec = {
    "tags": ["Inventory"],
    "summary": "Create product",
    "description": "Add a new product to inventory",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["ean", "name", "price"],
                "properties": {
                    "ean": {
                        "type": "string",
                        "minLength": 8,
                        "maxLength": 13,
                        "example": "1234567890123",
                        "description": "EAN-8 or EAN-13 barcode"
                    },
                    "name": {"type": "string", "example": "Coca Cola 330ml"},
                    "description": {"type": "string", "example": "Refreshing cola beverage"},
                    "price": {"type": "number", "example": 2.50},
                    "category": {"type": "string", "example": "beverages"},
                    "image_url": {"type": "string", "example": "https://example.com/coke.jpg"}
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "Product created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Validation error or duplicate EAN"},
        401: {"description": "Unauthorized"}
    }
}

update_product_spec = {
    "tags": ["Inventory"],
    "summary": "Update product",
    "description": "Update an existing product in inventory",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Product UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "ean": {"type": "string", "minLength": 8, "maxLength": 13},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "price": {"type": "number"},
                    "category": {"type": "string"},
                    "image_url": {"type": "string"}
                },
                "example": {
                    "price": 2.75,
                    "description": "Updated description"
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Product updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Validation or UUID error"},
        404: {"description": "Product not found"}
    }
}

delete_product_spec = {
    "tags": ["Inventory"],
    "summary": "Delete product",
    "description": "Remove a product from inventory",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Product UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Product deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"}
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Product not found"}
    }
}
