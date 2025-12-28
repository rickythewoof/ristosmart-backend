"""
Swagger/OpenAPI documentation for Order endpoints
"""

get_all_orders_spec = {
    "tags": ["Orders"],
    "summary": "Get all orders",
    "description": "Retrieve all orders with optional status filtering",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "status",
            "in": "query",
            "type": "string",
            "enum": ["pending", "confirmed", "preparing", "ready", "delivered", "completed", "cancelled"],
            "description": "Filter by order status"
        }
    ],
    "responses": {
        200: {
            "description": "Orders retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"type": "array"},
                    "count": {"type": "integer", "example": 25}
                }
            }
        },
        401: {"description": "Unauthorized"}
    }
}

get_order_spec = {
    "tags": ["Orders"],
    "summary": "Get order by ID",
    "description": "Retrieve a specific order with all its items",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Order retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Order not found"}
    }
}

create_order_spec = {
    "tags": ["Orders"],
    "summary": "Create new order",
    "description": "Create a new order with menu items (Waiter or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["order_type", "items"],
                "properties": {
                    "table_number": {"type": "integer", "example": 5},
                    "customer_name": {"type": "string", "example": "John Smith"},
                    "order_type": {"type": "string", "enum": ["dine_in", "takeaway", "delivery"], "example": "dine_in"},
                    "special_instructions": {"type": "string", "example": "Please rush, customer in a hurry"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["menu_item_id", "quantity"],
                            "properties": {
                                "menu_item_id": {"type": "string", "format": "uuid", "example": "123e4567-e89b-12d3-a456-426614174000"},
                                "quantity": {"type": "integer", "example": 2},
                                "special_instructions": {"type": "string", "example": "Extra cheese, no olives"}
                            }
                        }
                    }
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "Order created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Validation error or invalid menu item"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Waiter or Manager role required"}
    }
}

update_order_status_spec = {
    "tags": ["Orders"],
    "summary": "Update order status",
    "description": "Update the overall status of an order (Chef or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "confirmed", "preparing", "ready", "delivered", "completed", "cancelled"],
                        "example": "preparing"
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Order status updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Invalid status or UUID"},
        404: {"description": "Order not found"}
    }
}

update_order_item_status_spec = {
    "tags": ["Orders"],
    "summary": "Update order item status",
    "description": "Update the status of a specific item within an order (Chef or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order UUID"
        },
        {
            "name": "item_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order item UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "preparing", "ready", "served", "cancelled"],
                        "example": "ready"
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Order item status updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Invalid status or UUID"},
        404: {"description": "Order or item not found"}
    }
}

process_payment_spec = {
    "tags": ["Orders"],
    "summary": "Process payment",
    "description": "Process payment for an order and mark it as paid (Cashier or Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order UUID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["payment_method"],
                "properties": {
                    "payment_method": {
                        "type": "string",
                        "enum": ["cash", "card", "digital"],
                        "example": "card"
                    },
                    "amount_paid": {"type": "number", "example": 50.00}
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Payment processed successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
        },
        400: {"description": "Invalid payment data"},
        404: {"description": "Order not found"}
    }
}

delete_order_spec = {
    "tags": ["Orders"],
    "summary": "Delete order",
    "description": "Delete an order and all its items (Manager only)",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "string",
            "format": "uuid",
            "required": True,
            "description": "Order UUID"
        }
    ],
    "responses": {
        200: {
            "description": "Order deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"}
                }
            }
        },
        400: {"description": "Invalid UUID format"},
        404: {"description": "Order not found"}
    }
}
