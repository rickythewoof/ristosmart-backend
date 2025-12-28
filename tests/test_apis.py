#!/usr/bin/env python3
"""
Comprehensive API Test Suite for RistoSmart Backend
Tests all endpoints with proper authentication and authorization
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

load_dotenv(dotenv_path=env_path)


# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
HEADERS = {"Content-Type": "application/json"}

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Test statistics
stats = {
    'total': 0,
    'passed': 0,
    'failed': 0
}

def log_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {message}")

def log_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {message}")
    stats['passed'] += 1
    stats['total'] += 1

def log_error(message):
    """Print error message"""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {message}")
    stats['failed'] += 1
    stats['total'] += 1

def log_section(message):
    """Print section header"""
    print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")

def test_health_check():
    """Test health check endpoint"""
    log_section("TEST: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            log_success(f"Health check passed - Status: {response.status_code}")
            return True
        else:
            log_error(f"Health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Health check failed - Error: {str(e)}")
        return False

def login_user(username, password):
    """Login and return access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers=HEADERS,
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                log_success(f"Login successful for user: {username}")
                return token
        
        log_error(f"Login failed for user: {username} - Status: {response.status_code}")
        return None
    except Exception as e:
        log_error(f"Login exception for user: {username} - Error: {str(e)}")
        return None

def test_authentication():
    """Test authentication endpoints"""
    log_section("TEST: Authentication")
    
    # Test login with manager credentials
    log_info("Testing manager login...")
    token = login_user("manager", f"{os.getenv('MANAGER_PASSWORD', 'changemeplease!')}")
    
    if not token:
        log_error("Manager login failed - Cannot proceed with authenticated tests")
        return None
    
    # Test getting current user info
    log_info("Testing GET /api/users/me...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            log_success(f"GET /api/users/me - User: {user_data.get('user', {}).get('username')}")
        else:
            log_error(f"GET /api/users/me failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users/me exception - Error: {str(e)}")

    # Test accessing protected endpoint without token
    log_info("Testing unauthorized access (no token)...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/me", headers=HEADERS)

        if response.status_code == 401:
            log_success("Unauthorized access correctly blocked - Status: 401")
        else:
            log_error(f"Unauthorized access not blocked - Status: {response.status_code}")
    except Exception as e:
        log_error(f"Unauthorized access test exception - Error: {str(e)}")
    
    # Test with invalid token
    log_info("Testing invalid token...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={**HEADERS, "Authorization": "Bearer invalid_token_here"}
        )
        
        if response.status_code == 401 or response.status_code == 422:
            log_success(f"Invalid token correctly rejected - Status: {response.status_code}")
        else:
            log_error(f"Invalid token not rejected - Status: {response.status_code}")
    except Exception as e:
        log_error(f"Invalid token test exception - Error: {str(e)}")
    
    return token

def test_menu_items(token):
    """Test menu item endpoints"""
    log_section("TEST: Menu Items")
    
    created_item_id = None
    
    # Test GET all menu items (public)
    log_info("Testing GET /api/menu/ (public access)...")
    try:
        response = requests.get(f"{BASE_URL}/api/menu/")
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/menu/ - Retrieved {len(data.get('data', []))} items")
        else:
            log_error(f"GET /api/menu/ failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/menu/ exception - Error: {str(e)}")
    
    # Test GET available menu items (public)
    log_info("Testing GET /api/menu/available (public access)...")
    try:
        response = requests.get(f"{BASE_URL}/api/menu/available")
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/menu/available - Retrieved {len(data.get('data', []))} items")
        else:
            log_error(f"GET /api/menu/available failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/menu/available exception - Error: {str(e)}")
    
    # Test POST create menu item (protected)
    log_info("Testing POST /api/menu/ (create)...")
    menu_data = {
        "name": f"Test Dish {datetime.now().strftime('%H%M%S')}",
        "description": "Automated test dish",
        "price": 15.99,
        "category": "main",
        "preparation_time": 20,
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 450,
            "protein": 25
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/menu/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json=menu_data
        )
        
        if response.status_code == 201:
            data = response.json()
            created_item_id = data.get('data', {}).get('id')
            log_success(f"POST /api/menu/ - Created item ID: {created_item_id}")
        else:
            log_error(f"POST /api/menu/ failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/menu/ exception - Error: {str(e)}")
    
    # Test POST without authentication
    log_info("Testing POST /api/menu/ without authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/menu/",
            headers=HEADERS,
            json=menu_data
        )
        
        if response.status_code == 401:
            log_success("POST /api/menu/ correctly blocked without auth - Status: 401")
        else:
            log_error(f"POST /api/menu/ not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/menu/ no-auth test exception - Error: {str(e)}")
    
    if created_item_id:
        # Test GET single menu item
        log_info(f"Testing GET /api/menu/{created_item_id}...")
        try:
            response = requests.get(f"{BASE_URL}/api/menu/{created_item_id}")
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"GET /api/menu/{created_item_id} - Name: {data.get('data', {}).get('name')}")
            else:
                log_error(f"GET /api/menu/{created_item_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/menu/{created_item_id} exception - Error: {str(e)}")
        
        # Test PUT update menu item
        log_info(f"Testing PUT /api/menu/{created_item_id}...")
        update_data = {
            "price": 18.99,
            "is_available": False
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/api/menu/{created_item_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=update_data
            )
            
            if response.status_code == 200:
                log_success(f"PUT /api/menu/{created_item_id} - Updated successfully")
            else:
                log_error(f"PUT /api/menu/{created_item_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/menu/{created_item_id} exception - Error: {str(e)}")
        
        # Test PUT without authentication
        log_info(f"Testing PUT /api/menu/{created_item_id} without authentication...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/menu/{created_item_id}",
                headers=HEADERS,
                json=update_data
            )
            
            if response.status_code == 401:
                log_success(f"PUT /api/menu/{created_item_id} correctly blocked without auth")
            else:
                log_error(f"PUT /api/menu/{created_item_id} not blocked without auth - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/menu/{created_item_id} no-auth test exception - Error: {str(e)}")
        
        # Test DELETE menu item
        log_info(f"Testing DELETE /api/menu/{created_item_id}...")
        try:
            response = requests.delete(
                f"{BASE_URL}/api/menu/{created_item_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                log_success(f"DELETE /api/menu/{created_item_id} - Deleted successfully")
            else:
                log_error(f"DELETE /api/menu/{created_item_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"DELETE /api/menu/{created_item_id} exception - Error: {str(e)}")
    
    return created_item_id

def test_orders(token):
    """Test order endpoints"""
    log_section("TEST: Orders")
    
    created_order_id = None
    
    # First, create a menu item to use in order
    log_info("Creating test menu item for order...")
    menu_item_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/api/menu/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json={
                "name": "Test Pizza",
                "description": "Test pizza for order",
                "price": 12.50,
                "tax_amount": 0.1,
                "category": "main",
                "preparation_time": 15
            }
        )
        
        if response.status_code == 201:
            menu_item_id = response.json().get('data', {}).get('id')
            log_success(f"Test menu item created - ID: {menu_item_id}")
        else:
            log_error(f"Failed to create test menu item - Status: {response.status_code}")
    except Exception as e:
        log_error(f"Exception creating test menu item - Error: {str(e)}")
    
    if not menu_item_id:
        log_error("Cannot proceed with order tests without menu item")
        return None
    
    # Test GET all orders
    log_info("Testing GET /api/orders/...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/orders/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/orders/ - Retrieved {len(data.get('data', []))} orders")
        else:
            log_error(f"GET /api/orders/ failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/orders/ exception - Error: {str(e)}")
    
    # Test GET orders without authentication
    log_info("Testing GET /api/orders/ without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/orders/", headers=HEADERS)
        
        if response.status_code == 401:
            log_success("GET /api/orders/ correctly blocked without auth")
        else:
            log_error(f"GET /api/orders/ not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/orders/ no-auth test exception - Error: {str(e)}")
    
    # Test POST create order
    log_info("Testing POST /api/orders/ (create)...")
    order_data = {
        "table_number": 5,
        "customer_name": "Test Customer",
        "order_type": "dine_in",
        "items": [
            {
                "menu_item_id": menu_item_id,
                "quantity": 2,
                "special_instructions": "Extra cheese"
            }
        ],
        "special_instructions": "Please rush"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json=order_data
        )
        
        if response.status_code == 201:
            data = response.json()
            created_order_id = data.get('data', {}).get('id')
            order_number = data.get('data', {}).get('order_number')
            log_success(f"POST /api/orders/ - Created order {order_number}, ID: {created_order_id}")
        else:
            log_error(f"POST /api/orders/ failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/orders/ exception - Error: {str(e)}")
    
    # Test POST order without authentication
    log_info("Testing POST /api/orders/ without authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/",
            headers=HEADERS,
            json=order_data
        )
        
        if response.status_code == 401:
            log_success("POST /api/orders/ correctly blocked without auth")
        else:
            log_error(f"POST /api/orders/ not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/orders/ no-auth test exception - Error: {str(e)}")
    
    if created_order_id:
        # Test GET single order
        log_info(f"Testing GET /api/orders/{created_order_id}...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/orders/{created_order_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"GET /api/orders/{created_order_id} - Status: {data.get('data', {}).get('status')}")
            else:
                log_error(f"GET /api/orders/{created_order_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/orders/{created_order_id} exception - Error: {str(e)}")
        
        # Test PUT update order status
        log_info(f"Testing PUT /api/orders/{created_order_id}/status...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/orders/{created_order_id}/status",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json={"status": "confirmed"}
            )
            
            if response.status_code == 200:
                log_success(f"PUT /api/orders/{created_order_id}/status - Updated to confirmed")
            else:
                log_error(f"PUT /api/orders/{created_order_id}/status failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/orders/{created_order_id}/status exception - Error: {str(e)}")
        
        # Test PUT update order status without authentication
        log_info(f"Testing PUT /api/orders/{created_order_id}/status without authentication...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/orders/{created_order_id}/status",
                headers=HEADERS,
                json={"status": "preparing"}
            )
            
            if response.status_code == 401:
                log_success(f"PUT /api/orders/{created_order_id}/status correctly blocked without auth")
            else:
                log_error(f"PUT /api/orders/{created_order_id}/status not blocked - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/orders/{created_order_id}/status no-auth test exception - Error: {str(e)}")
        
        created_order_item_id = None
        # Get first order item with order ID equal to the created order ID
        log_info(f"Retrieving order items for order ID: {created_order_id}...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/orders/{created_order_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                order_items = response.json().get("data", {}).get("items", [])
                if order_items:
                    created_order_item_id = order_items[0].get("id")
                    log_success(f"Retrieved order item ID: {created_order_item_id}")
                else:
                    log_error("No order items found")
            else:
                log_error(f"Failed to retrieve order items - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/orders/{created_order_id} exception - Error: {str(e)}")

        # Test PUT update status on order items
        log_info(f"Testing PUT /api/orders/{created_order_id}/items/{created_order_item_id}/status...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/orders/{created_order_id}/items/{created_order_item_id}/status",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json={"status": "ready"}
            )

            if response.status_code == 200:
                log_success(f"PUT /api/orders/{created_order_id}/items/{created_order_item_id}/status - Updated to ready")
            else:
                log_error(f"PUT /api/orders/{created_order_id}/items/{created_order_item_id}/status failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/orders/{created_order_id}/items/{created_order_item_id}/status exception - Error: {str(e)}")
    
    # Clean up test menu item
    if menu_item_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/api/menu/{menu_item_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                log_success(f"DELETE /api/menu/{menu_item_id} - Deleted successfully")
            else:
                log_error(f"DELETE /api/menu/{menu_item_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"DELETE /api/menu/{menu_item_id} exception - Error: {str(e)}")

        except:
            pass
    
    return created_order_id

def test_user_management(token):
    """Test user management endpoints"""
    log_section("TEST: User Management")
    
    created_user_id = None
    new_user_token = None
    
    # Test GET all users (manager only)
    log_info("Testing GET /api/users (manager only)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/users - Retrieved {len(data.get('data', []))} users")
        else:
            log_error(f"GET /api/users failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users exception - Error: {str(e)}")
    
    # Test GET all users without authentication
    log_info("Testing GET /api/users without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", headers=HEADERS)
        
        if response.status_code == 401:
            log_success("GET /api/users correctly blocked without auth")
        else:
            log_error(f"GET /api/users not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users no-auth test exception - Error: {str(e)}")
    
    # Test POST register new user (manager only)
    log_info("Testing POST /api/auth/register (create user)...")
    user_data = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"testuser_{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "role": "waiter"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json=user_data
        )
        
        if response.status_code == 201:
            data = response.json()
            created_user_id = data.get('user', {}).get('id')
            log_success(f"POST /api/auth/register - Created user: {user_data['username']}")
        else:
            log_error(f"POST /api/auth/register failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/auth/register exception - Error: {str(e)}")
    
    # Test POST register without authentication
    log_info("Testing POST /api/auth/register without authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers=HEADERS,
            json=user_data
        )
        
        if response.status_code == 401:
            log_success("POST /api/auth/register correctly blocked without auth")
        else:
            log_error(f"POST /api/auth/register not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/auth/register no-auth test exception - Error: {str(e)}")
    
    # Test login with newly created user
    if created_user_id:
        log_info(f"Testing login with newly created user: {user_data['username']}...")
        new_user_token = login_user(user_data['username'], user_data['password'])
        
        if new_user_token:
            log_success(f"New user login successful: {user_data['username']}")
        else:
            log_error(f"New user login failed: {user_data['username']}")
    
    # Test GET current user
    if new_user_token:
        log_info("Testing GET /api/users/me...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/users/me",
                headers={**HEADERS, "Authorization": f"Bearer {new_user_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"GET /api/users/me - Retrieved user: {data.get('data', {}).get('username')}")
            else:
                log_error(f"GET /api/users/me failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/users/me exception - Error: {str(e)}")
    
    # Test GET specific user (manager only)
    if created_user_id:
        log_info(f"Testing GET /api/users/{created_user_id} (manager only)...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/users/{created_user_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                log_success(f"GET /api/users/{created_user_id} - User: {data.get('data', {}).get('username')}")
            else:
                log_error(f"GET /api/users/{created_user_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/users/{created_user_id} exception - Error: {str(e)}")
    
    # Test PATCH update user (manager only)
    if created_user_id:
        log_info(f"Testing PATCH /api/users/{created_user_id} (manager only)...")
        try:
            response = requests.patch(
                f"{BASE_URL}/api/users/{created_user_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json={"full_name": "Updated Test User"}
            )
            
            if response.status_code == 200:
                log_success(f"PATCH /api/users/{created_user_id} - Updated successfully")
            else:
                log_error(f"PATCH /api/users/{created_user_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PATCH /api/users/{created_user_id} exception - Error: {str(e)}")
    
    return created_user_id, new_user_token


def test_checkins(user_id, user_token):
    """Test check-in/check-out endpoints"""
    log_section("TEST: Check-ins")
    
    if not user_id or not user_token:
        log_error("Cannot test check-ins without valid user_id and token")
        return
    
    checkin_id = None
    
    # Test GET all check-ins for user
    log_info(f"Testing GET /api/users/{user_id}/checkins...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/{user_id}/checkins",
            headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/users/{user_id}/checkins - Retrieved {len(data.get('data', []))} check-ins")
        else:
            log_error(f"GET /api/users/{user_id}/checkins failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users/{user_id}/checkins exception - Error: {str(e)}")
    
    # Test GET check-ins without authentication
    log_info(f"Testing GET /api/users/{user_id}/checkins without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/{user_id}/checkins", headers=HEADERS)
        
        if response.status_code == 401:
            log_success("GET /api/users/{user_id}/checkins correctly blocked without auth")
        else:
            log_error(f"GET /api/users/{user_id}/checkins not blocked - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users/{user_id}/checkins no-auth test exception - Error: {str(e)}")
    
    # Test POST create check-in
    log_info(f"Testing POST /api/users/{user_id}/checkins (check-in)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/{user_id}/checkins",
            headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code == 201:
            data = response.json()
            checkin_id = data.get('data', {}).get('id')
            log_success(f"POST /api/users/{user_id}/checkins - Check-in created: {checkin_id}")
        else:
            log_error(f"POST /api/users/{user_id}/checkins failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/users/{user_id}/checkins exception - Error: {str(e)}")
    
    # Test POST check-in again (should fail - already checked in)
    log_info(f"Testing POST /api/users/{user_id}/checkins again (should fail)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/{user_id}/checkins",
            headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code == 400:
            log_success("POST /api/users/{user_id}/checkins correctly blocked - already checked in")
        else:
            log_error(f"POST /api/users/{user_id}/checkins not blocked - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/users/{user_id}/checkins second attempt exception - Error: {str(e)}")
    
    # Test GET current check-in
    log_info(f"Testing GET /api/users/{user_id}/checkins/current...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/{user_id}/checkins/current",
            headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/users/{user_id}/checkins/current - Active check-in found")
        else:
            log_error(f"GET /api/users/{user_id}/checkins/current failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users/{user_id}/checkins/current exception - Error: {str(e)}")
    
    # Test GET specific check-in
    if checkin_id:
        log_info(f"Testing GET /api/users/{user_id}/checkins/{checkin_id}...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/users/{user_id}/checkins/{checkin_id}",
                headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
            )
            
            if response.status_code == 200:
                log_success(f"GET /api/users/{user_id}/checkins/{checkin_id} - Retrieved check-in")
            else:
                log_error(f"GET /api/users/{user_id}/checkins/{checkin_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/users/{user_id}/checkins/{checkin_id} exception - Error: {str(e)}")
    
    # Test PUT update check-in (check-out)
    if checkin_id:
        log_info(f"Testing PUT /api/users/{user_id}/checkins/{checkin_id} (check-out)...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/users/{user_id}/checkins/{checkin_id}",
                headers={**HEADERS, "Authorization": f"Bearer {user_token}"},
                json={}
            )
            
            if response.status_code == 200:
                log_success(f"PUT /api/users/{user_id}/checkins/{checkin_id} - Check-out successful")
            else:
                log_error(f"PUT /api/users/{user_id}/checkins/{checkin_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/users/{user_id}/checkins/{checkin_id} exception - Error: {str(e)}")
    
    # Test PUT check-out again (should fail - already checked out)
    if checkin_id:
        log_info(f"Testing PUT /api/users/{user_id}/checkins/{checkin_id} again (should fail)...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/users/{user_id}/checkins/{checkin_id}",
                headers={**HEADERS, "Authorization": f"Bearer {user_token}"},
                json={}
            )
            
            if response.status_code == 400:
                log_success(f"PUT /api/users/{user_id}/checkins/{checkin_id} correctly blocked - already checked out")
            else:
                log_error(f"PUT /api/users/{user_id}/checkins/{checkin_id} not blocked - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/users/{user_id}/checkins/{checkin_id} second attempt exception - Error: {str(e)}")
    
    # Test GET current check-in (should fail - no active check-in)
    log_info(f"Testing GET /api/users/{user_id}/checkins/current (should fail - no active)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/{user_id}/checkins/current",
            headers={**HEADERS, "Authorization": f"Bearer {user_token}"}
        )
        
        if response.status_code == 404:
            log_success(f"GET /api/users/{user_id}/checkins/current correctly returns 404")
        else:
            log_error(f"GET /api/users/{user_id}/checkins/current should return 404 - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/users/{user_id}/checkins/current no-active test exception - Error: {str(e)}")
    
    return checkin_id

def test_inventory(token):
    """Test inventory/product endpoints"""
    log_section("TEST: Inventory/Products")
    
    created_product_id = None
    
    # Test GET all products
    log_info("Testing GET /api/inventory/...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/inventory/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"GET /api/inventory/ - Retrieved {data.get('count', 0)} products")
        else:
            log_error(f"GET /api/inventory/ failed - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/inventory/ exception - Error: {str(e)}")
    
    # Test GET all products without authentication
    log_info("Testing GET /api/inventory/ without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/", headers=HEADERS)
        
        if response.status_code == 401:
            log_success("GET /api/inventory/ correctly blocked without auth")
        else:
            log_error(f"GET /api/inventory/ not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"GET /api/inventory/ no-auth test exception - Error: {str(e)}")
    
    # Test POST create product
    log_info("Testing POST /api/inventory/ (create product)...")
    # Generate EAN-13 (13 digits) with timestamp to make it unique
    timestamp = datetime.now().strftime('%S%f')[:5]  # Get 5 digits from seconds+microseconds
    product_data = {
        "ean": f"12345678{timestamp}",  # EAN-13: 8 fixed + 5 variable = 13 digits
        "name": f"Test Product {datetime.now().strftime('%H%M%S')}",
        "description": "Automated test product",
        "price": 25.99,
        "category": "beverages",
        "image_url": "https://example.com/product.jpg"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/inventory/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json=product_data
        )
        
        if response.status_code == 201:
            data = response.json()
            created_product_id = data.get('data', {}).get('id')
            log_success(f"POST /api/inventory/ - Created product ID: {created_product_id}")
        else:
            log_error(f"POST /api/inventory/ failed - Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_error(f"POST /api/inventory/ exception - Error: {str(e)}")
    
    # Test POST create product with invalid data (missing required fields)
    log_info("Testing POST /api/inventory/ with invalid data (missing fields)...")
    invalid_product_data = {
        "name": "Invalid Product"
        # Missing ean and price (required fields)
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/inventory/",
            headers={**HEADERS, "Authorization": f"Bearer {token}"},
            json=invalid_product_data
        )
        
        if response.status_code == 400:
            log_success("POST /api/inventory/ correctly rejected invalid data - Status: 400")
        else:
            log_error(f"POST /api/inventory/ should reject invalid data - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/inventory/ invalid data test exception - Error: {str(e)}")
    
    # Test POST create product with duplicate EAN
    if created_product_id:
        log_info("Testing POST /api/inventory/ with duplicate EAN...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/inventory/",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=product_data  # Same EAN as before
            )
            
            if response.status_code == 409:
                log_success("POST /api/inventory/ correctly rejected duplicate EAN - Status: 409")
            else:
                log_error(f"POST /api/inventory/ should reject duplicate EAN - Status: {response.status_code}")
        except Exception as e:
            log_error(f"POST /api/inventory/ duplicate EAN test exception - Error: {str(e)}")
    
    # Test POST without authentication
    log_info("Testing POST /api/inventory/ without authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/inventory/",
            headers=HEADERS,
            json=product_data
        )
        
        if response.status_code == 401:
            log_success("POST /api/inventory/ correctly blocked without auth")
        else:
            log_error(f"POST /api/inventory/ not blocked without auth - Status: {response.status_code}")
    except Exception as e:
        log_error(f"POST /api/inventory/ no-auth test exception - Error: {str(e)}")
    
    if created_product_id:
        # Test GET single product
        log_info(f"Testing GET /api/inventory/{created_product_id}...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                product_name = data.get('data', {}).get('name')
                log_success(f"GET /api/inventory/{created_product_id} - Name: {product_name}")
            else:
                log_error(f"GET /api/inventory/{created_product_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/inventory/{created_product_id} exception - Error: {str(e)}")
        
        # Test GET single product with invalid UUID
        log_info("Testing GET /api/inventory/invalid-uuid...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/inventory/invalid-uuid-123",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 400:
                log_success("GET /api/inventory/invalid-uuid correctly rejected - Status: 400")
            else:
                log_error(f"GET /api/inventory/invalid-uuid should return 400 - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/inventory/invalid-uuid exception - Error: {str(e)}")
        
        # Test GET non-existent product
        log_info("Testing GET /api/inventory/00000000-0000-0000-0000-000000000000...")
        try:
            response = requests.get(
                f"{BASE_URL}/api/inventory/00000000-0000-0000-0000-000000000000",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 404:
                log_success("GET /api/inventory/non-existent correctly returned 404")
            else:
                log_error(f"GET /api/inventory/non-existent should return 404 - Status: {response.status_code}")
        except Exception as e:
            log_error(f"GET /api/inventory/non-existent exception - Error: {str(e)}")
        
        # Test PUT update product
        log_info(f"Testing PUT /api/inventory/{created_product_id}...")
        update_data = {
            "price": 29.99,
            "description": "Updated test product description",
            "category": "food"
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                updated_price = data.get('data', {}).get('price')
                log_success(f"PUT /api/inventory/{created_product_id} - Updated price: €{updated_price}")
            else:
                log_error(f"PUT /api/inventory/{created_product_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/inventory/{created_product_id} exception - Error: {str(e)}")
        
        # Test PUT update product with invalid data
        log_info(f"Testing PUT /api/inventory/{created_product_id} with invalid data...")
        invalid_update_data = {
            "price": -10.00  # Negative price should be rejected
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"},
                json=invalid_update_data
            )
            
            if response.status_code == 400:
                log_success(f"PUT /api/inventory/{created_product_id} correctly rejected invalid price")
            else:
                log_error(f"PUT /api/inventory/{created_product_id} should reject negative price - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/inventory/{created_product_id} invalid data test exception - Error: {str(e)}")
        
        # Test PUT without authentication
        log_info(f"Testing PUT /api/inventory/{created_product_id} without authentication...")
        try:
            response = requests.put(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers=HEADERS,
                json=update_data
            )
            
            if response.status_code == 401:
                log_success(f"PUT /api/inventory/{created_product_id} correctly blocked without auth")
            else:
                log_error(f"PUT /api/inventory/{created_product_id} not blocked without auth - Status: {response.status_code}")
        except Exception as e:
            log_error(f"PUT /api/inventory/{created_product_id} no-auth test exception - Error: {str(e)}")
        
        # Test DELETE product
        log_info(f"Testing DELETE /api/inventory/{created_product_id}...")
        try:
            response = requests.delete(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                log_success(f"DELETE /api/inventory/{created_product_id} - Deleted successfully")
            else:
                log_error(f"DELETE /api/inventory/{created_product_id} failed - Status: {response.status_code}")
        except Exception as e:
            log_error(f"DELETE /api/inventory/{created_product_id} exception - Error: {str(e)}")
        
        # Test DELETE non-existent product
        log_info(f"Testing DELETE /api/inventory/{created_product_id} again (should fail)...")
        try:
            response = requests.delete(
                f"{BASE_URL}/api/inventory/{created_product_id}",
                headers={**HEADERS, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 404:
                log_success(f"DELETE /api/inventory/{created_product_id} correctly returned 404 - already deleted")
            else:
                log_error(f"DELETE /api/inventory/{created_product_id} should return 404 - Status: {response.status_code}")
        except Exception as e:
            log_error(f"DELETE /api/inventory/{created_product_id} second delete exception - Error: {str(e)}")
        
        # Test DELETE without authentication
        log_info("Testing DELETE /api/inventory/00000000-0000-0000-0000-000000000000 without authentication...")
        try:
            response = requests.delete(
                f"{BASE_URL}/api/inventory/00000000-0000-0000-0000-000000000000",
                headers=HEADERS
            )
            
            if response.status_code == 401:
                log_success("DELETE /api/inventory/ correctly blocked without auth")
            else:
                log_error(f"DELETE /api/inventory/ not blocked without auth - Status: {response.status_code}")
        except Exception as e:
            log_error(f"DELETE /api/inventory/ no-auth test exception - Error: {str(e)}")
    
    return created_product_id

def print_summary():
    """Print test summary"""
    log_section("TEST SUMMARY")
    
    total = stats['total']
    passed = stats['passed']
    failed = stats['failed']
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests:  {total}")
    print(f"Passed:       {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"Failed:       {Colors.RED}{failed}{Colors.RESET}")
    print(f"Pass Rate:    {pass_rate:.1f}%")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}All tests passed!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}Some tests failed. Please review the output above.{Colors.RESET}")
        return 1

def main():
    """Main test runner"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}RistoSmart API Comprehensive Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}Base URL: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    # Check if server is running
    if not test_health_check():
        log_error("Server is not running. Please start the backend first.")
        sys.exit(1)
    
    # Test authentication and get token
    token = test_authentication()
    if not token:
        log_error("Authentication failed. Cannot proceed with authenticated tests.")
        sys.exit(1)
    
    # Test menu items
    test_menu_items(token)
    
    # Test orders
    test_orders(token)
    
    # Test inventory/products
    test_inventory(token)
        
    # Test user management
    created_user_id, new_user_token = test_user_management(token)
    
    # Test check-ins with the newly created user
    if created_user_id and new_user_token:
        test_checkins(created_user_id, new_user_token)
    else:
        log_error("Skipping check-in tests - no valid user created")
    
    # Print summary
    exit_code = print_summary()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
