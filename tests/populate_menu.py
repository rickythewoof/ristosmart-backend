"""
Script to populate the database with sample menu items
Run with: python backend/tests/populate_menu.py
"""
import requests
import json
import sys
import os

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
API_URL = f"{BASE_URL}/api"

# Manager credentials for authentication
MANAGER_USERNAME = "manager"
MANAGER_PASSWORD = os.getenv('MANAGER_PASSWORD', 'changemeplease!')

# Sample menu items
MENU_ITEMS = [
    # Antipasti (Appetizers)
    {
        "name": "Bruschetta Classica",
        "description": "Pane tostato con pomodori freschi, basilico e aglio",
        "price": 6.50,
        "category": "appetizer",
        "allergens": ["gluten"],
        "nutritional_info": {
            "calories": 180,
            "protein": 5,
            "carbs": 25,
            "fat": 7
        },
        "preparation_time": 10,
        "is_available": True
    },
    {
        "name": "Caprese",
        "description": "Mozzarella di bufala, pomodori freschi, basilico e olio EVO",
        "price": 8.90,
        "category": "appetizer",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 220,
            "protein": 12,
            "carbs": 8,
            "fat": 16
        },
        "preparation_time": 8,
        "is_available": True
    },
    {
        "name": "Prosciutto e Melone",
        "description": "Prosciutto crudo di Parma con melone cantalupo",
        "price": 9.50,
        "category": "appetizer",
        "allergens": [],
        "nutritional_info": {
            "calories": 160,
            "protein": 10,
            "carbs": 12,
            "fat": 8
        },
        "preparation_time": 5,
        "is_available": True
    },
    {
        "name": "Tagliere Misto",
        "description": "Selezione di salumi e formaggi italiani con miele e marmellata",
        "price": 14.90,
        "category": "appetizer",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 420,
            "protein": 22,
            "carbs": 15,
            "fat": 32
        },
        "preparation_time": 10,
        "is_available": True
    },
    
    # Primi Piatti (First Courses)
    {
        "name": "Spaghetti alla Carbonara",
        "description": "Spaghetti con guanciale, uova, pecorino romano e pepe nero",
        "price": 12.50,
        "category": "main",
        "allergens": ["gluten", "eggs", "dairy"],
        "nutritional_info": {
            "calories": 580,
            "protein": 24,
            "carbs": 68,
            "fat": 22
        },
        "preparation_time": 15,
        "is_available": True
    },
    {
        "name": "Risotto ai Funghi Porcini",
        "description": "Risotto cremoso con funghi porcini freschi e parmigiano",
        "price": 14.00,
        "category": "main",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 520,
            "protein": 16,
            "carbs": 72,
            "fat": 18
        },
        "preparation_time": 20,
        "is_available": True
    },
    {
        "name": "Lasagne alla Bolognese",
        "description": "Lasagne fatte in casa con ragù di carne e besciamella",
        "price": 13.50,
        "category": "main",
        "allergens": ["gluten", "dairy", "eggs"],
        "nutritional_info": {
            "calories": 650,
            "protein": 28,
            "carbs": 58,
            "fat": 32
        },
        "preparation_time": 25,
        "is_available": True
    },
    {
        "name": "Penne all'Arrabbiata",
        "description": "Penne con pomodoro piccante, aglio e prezzemolo",
        "price": 10.50,
        "category": "main",
        "allergens": ["gluten"],
        "nutritional_info": {
            "calories": 450,
            "protein": 14,
            "carbs": 78,
            "fat": 10
        },
        "preparation_time": 12,
        "is_available": True
    },
    {
        "name": "Ravioli Ricotta e Spinaci",
        "description": "Ravioli fatti in casa con ricotta e spinaci al burro e salvia",
        "price": 13.00,
        "category": "main",
        "allergens": ["gluten", "dairy", "eggs"],
        "nutritional_info": {
            "calories": 520,
            "protein": 20,
            "carbs": 62,
            "fat": 20
        },
        "preparation_time": 15,
        "is_available": True
    },
    {
        "name": "Gnocchi al Pesto",
        "description": "Gnocchi di patate con pesto genovese fatto in casa",
        "price": 11.50,
        "category": "main",
        "allergens": ["gluten", "dairy", "nuts"],
        "nutritional_info": {
            "calories": 480,
            "protein": 15,
            "carbs": 65,
            "fat": 18
        },
        "preparation_time": 12,
        "is_available": True
    },
    
    # Secondi Piatti (Main Courses)
    {
        "name": "Tagliata di Manzo",
        "description": "Tagliata di manzo con rucola, grana e pomodorini",
        "price": 18.90,
        "category": "main",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 420,
            "protein": 45,
            "carbs": 8,
            "fat": 22
        },
        "preparation_time": 18,
        "is_available": True
    },
    {
        "name": "Costata alla Fiorentina",
        "description": "Costata di manzo alla griglia (800g circa)",
        "price": 28.00,
        "category": "main",
        "allergens": [],
        "nutritional_info": {
            "calories": 780,
            "protein": 85,
            "carbs": 2,
            "fat": 48
        },
        "preparation_time": 25,
        "is_available": True
    },
    {
        "name": "Pollo alla Cacciatora",
        "description": "Pollo in umido con pomodoro, olive e capperi",
        "price": 14.50,
        "category": "main",
        "allergens": [],
        "nutritional_info": {
            "calories": 380,
            "protein": 42,
            "carbs": 12,
            "fat": 18
        },
        "preparation_time": 20,
        "is_available": True
    },
    {
        "name": "Branzino al Sale",
        "description": "Branzino intero cotto al sale con verdure di stagione",
        "price": 22.00,
        "category": "main",
        "allergens": ["fish"],
        "nutritional_info": {
            "calories": 280,
            "protein": 48,
            "carbs": 5,
            "fat": 8
        },
        "preparation_time": 30,
        "is_available": True
    },
    {
        "name": "Salmone alla Griglia",
        "description": "Filetto di salmone con limone e erbe aromatiche",
        "price": 16.50,
        "category": "main",
        "allergens": ["fish"],
        "nutritional_info": {
            "calories": 320,
            "protein": 38,
            "carbs": 2,
            "fat": 18
        },
        "preparation_time": 15,
        "is_available": True
    },
    {
        "name": "Scaloppine al Limone",
        "description": "Scaloppine di vitello con salsa al limone",
        "price": 15.50,
        "category": "main",
        "allergens": ["gluten"],
        "nutritional_info": {
            "calories": 350,
            "protein": 36,
            "carbs": 12,
            "fat": 16
        },
        "preparation_time": 15,
        "is_available": True
    },
    
    # Pizza
    {
        "name": "Pizza Margherita",
        "description": "Pomodoro, mozzarella, basilico e olio EVO",
        "price": 8.00,
        "category": "main",
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 550,
            "protein": 22,
            "carbs": 72,
            "fat": 18
        },
        "preparation_time": 12,
        "is_available": True
    },
    {
        "name": "Pizza Diavola",
        "description": "Pomodoro, mozzarella e salame piccante",
        "price": 9.50,
        "category": "main",
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 620,
            "protein": 26,
            "carbs": 74,
            "fat": 24
        },
        "preparation_time": 12,
        "is_available": True
    },
    {
        "name": "Pizza Quattro Stagioni",
        "description": "Pomodoro, mozzarella, prosciutto, funghi, carciofi e olive",
        "price": 11.00,
        "category": "main",
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 640,
            "protein": 28,
            "carbs": 76,
            "fat": 22
        },
        "preparation_time": 14,
        "is_available": True
    },
    {
        "name": "Pizza Capricciosa",
        "description": "Pomodoro, mozzarella, prosciutto cotto, funghi e carciofi",
        "price": 10.50,
        "category": "main",
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 610,
            "protein": 27,
            "carbs": 75,
            "fat": 21
        },
        "preparation_time": 14,
        "is_available": True
    },
    {
        "name": "Pizza Bufalina",
        "description": "Pomodoro, mozzarella di bufala DOP, basilico",
        "price": 12.00,
        "category": "main",
        "allergens": ["gluten", "dairy"],
        "nutritional_info": {
            "calories": 580,
            "protein": 24,
            "carbs": 72,
            "fat": 20
        },
        "preparation_time": 12,
        "is_available": True
    },
    
    # Contorni (Side Dishes)
    {
        "name": "Insalata Mista",
        "description": "Insalata verde con pomodori, carote e cipolla",
        "price": 4.50,
        "category": "side",
        "allergens": [],
        "nutritional_info": {
            "calories": 45,
            "protein": 2,
            "carbs": 8,
            "fat": 1
        },
        "preparation_time": 5,
        "is_available": True
    },
    {
        "name": "Patate al Forno",
        "description": "Patate al forno con rosmarino e olio EVO",
        "price": 5.00,
        "category": "side",
        "allergens": [],
        "nutritional_info": {
            "calories": 180,
            "protein": 3,
            "carbs": 32,
            "fat": 6
        },
        "preparation_time": 25,
        "is_available": True
    },
    {
        "name": "Verdure Grigliate",
        "description": "Mix di verdure di stagione alla griglia",
        "price": 5.50,
        "category": "side",
        "allergens": [],
        "nutritional_info": {
            "calories": 95,
            "protein": 3,
            "carbs": 12,
            "fat": 4
        },
        "preparation_time": 15,
        "is_available": True
    },
    {
        "name": "Spinaci Saltati",
        "description": "Spinaci saltati in padella con aglio e olio",
        "price": 4.50,
        "category": "side",
        "allergens": [],
        "nutritional_info": {
            "calories": 85,
            "protein": 4,
            "carbs": 8,
            "fat": 5
        },
        "preparation_time": 8,
        "is_available": True
    },
    
    # Dolci (Desserts)
    {
        "name": "Tiramisù",
        "description": "Tiramisù fatto in casa con savoiardi e mascarpone",
        "price": 6.50,
        "category": "dessert",
        "allergens": ["gluten", "dairy", "eggs"],
        "nutritional_info": {
            "calories": 420,
            "protein": 8,
            "carbs": 48,
            "fat": 22
        },
        "preparation_time": 5,
        "is_available": True
    },
    {
        "name": "Panna Cotta",
        "description": "Panna cotta con coulis di frutti di bosco",
        "price": 5.50,
        "category": "dessert",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 320,
            "protein": 5,
            "carbs": 32,
            "fat": 18
        },
        "preparation_time": 5,
        "is_available": True
    },
    {
        "name": "Cheesecake",
        "description": "Cheesecake ai frutti di bosco",
        "price": 6.00,
        "category": "dessert",
        "allergens": ["gluten", "dairy", "eggs"],
        "nutritional_info": {
            "calories": 450,
            "protein": 8,
            "carbs": 42,
            "fat": 28
        },
        "preparation_time": 5,
        "is_available": True
    },
    {
        "name": "Gelato Artigianale",
        "description": "3 gusti a scelta",
        "price": 5.00,
        "category": "dessert",
        "allergens": ["dairy"],
        "nutritional_info": {
            "calories": 280,
            "protein": 6,
            "carbs": 38,
            "fat": 12
        },
        "preparation_time": 3,
        "is_available": True
    },
    
    # Bevande (Drinks)
    {
        "name": "Acqua Naturale",
        "description": "Acqua minerale naturale 1L",
        "price": 2.00,
        "category": "beverage",
        "allergens": [],
        "nutritional_info": {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Acqua Frizzante",
        "description": "Acqua minerale frizzante 1L",
        "price": 2.00,
        "category": "beverage",
        "allergens": [],
        "nutritional_info": {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Coca Cola",
        "description": "Coca Cola 33cl",
        "price": 3.00,
        "category": "beverage",
        "allergens": [],
        "nutritional_info": {
            "calories": 139,
            "protein": 0,
            "carbs": 35,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Birra Moretti",
        "description": "Birra Moretti 33cl",
        "price": 4.00,
        "category": "beverage",
        "allergens": ["gluten"],
        "nutritional_info": {
            "calories": 142,
            "protein": 1,
            "carbs": 12,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Vino Rosso della Casa",
        "description": "Vino rosso della casa (calice 15cl)",
        "price": 5.00,
        "category": "beverage",
        "allergens": ["sulfites"],
        "nutritional_info": {
            "calories": 112,
            "protein": 0,
            "carbs": 4,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Vino Bianco della Casa",
        "description": "Vino bianco della casa (calice 15cl)",
        "price": 5.00,
        "category": "beverage",
        "allergens": ["sulfites"],
        "nutritional_info": {
            "calories": 110,
            "protein": 0,
            "carbs": 5,
            "fat": 0
        },
        "preparation_time": 1,
        "is_available": True
    },
    {
        "name": "Caffè Espresso",
        "description": "Caffè espresso italiano",
        "price": 1.50,
        "category": "beverage",
        "allergens": [],
        "nutritional_info": {
            "calories": 2,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        },
        "preparation_time": 2,
        "is_available": True
    }
]


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


def create_menu_item(token, item):
    """Create a single menu item"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"  → POST {API_URL}/menu/")
    print(f"  → Item: {item['name']}")
    
    response = requests.post(
        f"{API_URL}/menu/",  # Added trailing slash
        json=item,
        headers=headers,
        allow_redirects=False  # Don't follow redirects
    )
    
    print(f"  ← Status: {response.status_code}")
    
    if response.status_code == 201:
        return True, response.json()
    else:
        # Print more debug info
        print(f"  ← Response: {response.text[:200]}")
        return False, f"Status {response.status_code}: {response.text}"


def main():
    print("=" * 60)
    print("RistoSmart - Menu Population Script")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Total items to create: {len(MENU_ITEMS)}")
    print("=" * 60)
    
    # Login
    token = login()
    
    # Create menu items
    print(f"\nCreating {len(MENU_ITEMS)} menu items...")
    success_count = 0
    failed_count = 0
    
    for idx, item in enumerate(MENU_ITEMS, 1):
        success, result = create_menu_item(token, item)
        
        if success:
            print(f"✓ [{idx}/{len(MENU_ITEMS)}] Created: {item['name']}")
            success_count += 1
        else:
            print(f"✗ [{idx}/{len(MENU_ITEMS)}] Failed: {item['name']}")
            print(f"  Error: {result}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully created: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total: {len(MENU_ITEMS)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
