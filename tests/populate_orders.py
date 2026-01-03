"""
Script to populate the database with sample orders
Run with: python backend/tests/populate_orders.py
"""
import requests
import json
import sys
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv


project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

load_dotenv(dotenv_path=env_path)

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
API_URL = f"{BASE_URL}/api"

# Manager credentials for authentication
MANAGER_USERNAME = "manager"
MANAGER_PASSWORD = os.getenv('MANAGER_PASSWORD', 'changemeplease!')



# Sample table numbers
TABLE_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 21, 22, 25]

# Sample customer names
CUSTOMER_NAMES = [
    "Mario Rossi",
    "Luigi Bianchi",
    "Giuseppe Verdi",
    "Anna Ferrari",
    "Maria Romano",
    "Francesco Ricci",
    "Laura Esposito",
    "Antonio Colombo",
    "Giulia Rizzo",
    "Marco Fontana",
    "Elena Greco",
    "Alessandro Conti",
    "Chiara Bruno",
    "Davide De Luca",
    "Sara Gallo",
    None,  # Some orders without customer name
    None,
    None
]

# Order types
ORDER_TYPES = ["dine_in", "takeout", "delivery"]

# Sample order statuses (for demonstration)
ORDER_STATUSES = ["preparing", "ready", "delivered"]


def login():
    """Login and get access token"""
    print(f"Logging in as {MANAGER_USERNAME}...")
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": MANAGER_USERNAME, "password": MANAGER_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Login successful")
        return data.get('access_token')
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)


def get_menu_items(token):
    """Get all available menu items"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_URL}/menu/available",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('data', [])
        print(f"✓ Retrieved {len(items)} menu items")
        return items
    else:
        print(f"✗ Failed to get menu items: {response.status_code}")
        return []


def create_order(token, order_data):
    """Create a single order"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/orders/",
        json=order_data,
        headers=headers,
        allow_redirects=False
    )
    
    if response.status_code == 201:
        return True, response.json()
    else:
        return False, f"Status {response.status_code}: {response.text}"


def generate_random_order(menu_items):
    """Generate a random order with random items"""
    # Random number of items (1-5)
    num_items = random.randint(1, 5)
    
    # Select random menu items
    selected_items = random.sample(menu_items, min(num_items, len(menu_items)))
    
    # Build order items
    order_items = []
    for item in selected_items:
        order_items.append({
            "menu_item_id": item['id'],
            "quantity": random.randint(1, 3),
            "special_instructions": random.choice([
                None,
                "No sale",
                "Piccante",
                "Ben cotto",
                "Al sangue",
                "Senza cipolla",
                "Extra formaggio"
            ])
        })
    
    # Build order
    order = {
        "table_number": random.choice(TABLE_NUMBERS),
        "customer_name": random.choice(CUSTOMER_NAMES),
        "order_type": random.choice(ORDER_TYPES),
        "items": order_items,
        "special_instructions": random.choice([
            None,
            "Allergico al glutine",
            "Portare tutto insieme",
            "Separare i piatti",
            "Cliente abituale"
        ])
    }
    
    return order


def main():
    print("=" * 60)
    print("RistoSmart - Orders Population Script")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print("=" * 60)
    
    # Login
    token = login()
    
    # Get menu items
    menu_items = get_menu_items(token)
    
    if not menu_items:
        print("✗ No menu items available. Please run populate_menu.py first!")
        sys.exit(1)
    
    # Ask how many orders to create
    try:
        num_orders = int(input(f"\nHow many orders do you want to create? (1-50): ") or "10")
        num_orders = max(1, min(50, num_orders))  # Limit between 1 and 50
    except ValueError:
        num_orders = 10
        print(f"Using default: {num_orders} orders")
    
    print(f"\nCreating {num_orders} random orders...")
    success_count = 0
    failed_count = 0
    
    for idx in range(1, num_orders + 1):
        order = generate_random_order(menu_items)
        success, result = create_order(token, order)
        
        if success:
            order_data = result.get('data', {})
            order_number = order_data.get('order_number', 'N/A')
            total = order_data.get('final_amount', 0)
            print(f"✓ [{idx}/{num_orders}] Created order #{order_number} - Table {order['table_number']} - €{total:.2f}")
            success_count += 1
        else:
            print(f"✗ [{idx}/{num_orders}] Failed to create order")
            print(f"  Error: {result}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully created: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total: {num_orders}")
    print("=" * 60)
    
    # Additional info
    if success_count > 0:
        print("\n💡 Tip: Use Swagger UI to view and manage orders:")
        print(f"   {BASE_URL}/docs")
        print("\n💡 Or use the API directly:")
        print(f"   GET {API_URL}/orders/")


if __name__ == "__main__":
    main()
