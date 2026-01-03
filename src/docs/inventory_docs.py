"""
Swagger/OpenAPI documentation for Inventory endpoints
"""

get_all_products_spec = {
                            "name": {"type": "string", "example": "Coca Cola 330ml"},
                            "description": {"type": "string"},
                            "price": {"type": "number", "example": 2.50},
                            "quantity": {"type": "integer", "example": 100},
                            "category": {"type": "string", "example": "beverages"},
                            "image_url": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"},
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
                                "quantity": {"type": "integer", "example": 100},
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

get_product_ean_spec = {
    "tags": ["Inventory"],
    "summary": "Search products by EAN",
    "description": "Retrieve products matching the given EAN code",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "ean",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "EAN code to search for"
        }
    ],
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
                                "quantity": {"type": "integer", "example": 100},
                                "category": {"type": "string", "example": "beverages"},
                                "image_url": {"type": "string"},
                                "created_at": {"type": "string", "format": "date-time"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "count": {"type": "integer", "example": 5}
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
                            "quantity": {"type": "integer", "example": 100},
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
    "description": "Update one or more fields of an existing product",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "type": "string",
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
                    "ean": {"type": "string", "example": "1234567890123"},
                    "name": {"type": "string", "example": "Coca Cola 330ml"},
                    "description": {"type": "string"},
                    "price": {"type": "number", "example": 2.50},
                    "quantity": {"type": "integer", "example": 150},
                    "category": {"type": "string", "example": "beverages"},
                    "image_url": {"type": "string"}
                },
                "description": "Only include fields you want to update. Example for quantity only: {\"quantity\": 150}"
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
                    "message": {"type": "string", "example": "Product updated successfully"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "ean": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "price": {"type": "number"},
                            "quantity": {"type": "integer"},
                            "category": {"type": "string"},
                            "image_url": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        },
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Product not found"},
        409: {"description": "EAN already exists"}
    }
}

modify_quantity_spec = {
    "tags": ["Inventory"],
    "summary": "Modify product quantity",
    "description": "Perform quantity operations: add (increment), remove (decrement), or set (absolute value). Useful for stock management, sales tracking, and inventory adjustments.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "Product UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["operation", "amount"],
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "remove", "set"],
                        "description": "Operation type: 'add' for stock replenishment, 'remove' for consumption/sales, 'set' for inventory count",
                        "example": "add"
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Amount to add, remove, or set. Must be positive for add/remove, non-negative for set",
                        "example": 50
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Quantity modified successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string", "example": "Quantity updated: 100 → 150"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "ean": {"type": "string", "example": "5449000000996"},
                            "name": {"type": "string", "example": "Coca Cola 330ml"},
                            "description": {"type": "string"},
                            "price": {"type": "number", "example": 1.50},
                            "quantity": {"type": "integer", "example": 150},
                            "category": {"type": "string", "example": "beverages"},
                            "image_url": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            },
            "examples": {
                "application/json": {
                    "add_operation": {
                        "description": "Add 50 units (stock replenishment)",
                        "value": {
                            "operation": "add",
                            "amount": 50
                        }
                    },
                    "remove_operation": {
                        "description": "Remove 10 units (consumption/sale)",
                        "value": {
                            "operation": "remove",
                            "amount": 10
                        }
                    },
                    "set_operation": {
                        "description": "Set to 100 units (physical inventory count)",
                        "value": {
                            "operation": "set",
                            "amount": 100
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation error or insufficient quantity",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "Insufficient quantity. Available: 5, Requested: 10"}
                }
            }
        },
        401: {"description": "Unauthorized - Missing or invalid token"},
        403: {"description": "Insufficient permissions - Requires product.edit permission"},
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
