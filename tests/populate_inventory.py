"""
Script to populate the database with sample inventory products
Run with: python backend/tests/populate_inventory.py
"""
import requests
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv


project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

load_dotenv(dotenv_path=env_path)

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
API_URL = f"{BASE_URL}/api"

# Manager credentials for authentication
MANAGER_USERNAME = "manager"
MANAGER_PASSWORD = os.getenv('MANAGER_PASSWORD', 'changemeplease!')

# Sample inventory products for an Italian restaurant
INVENTORY_PRODUCTS = [
    # Bevande (Beverages)
    {
        "ean": "5449000000996",
        "name": "Coca Cola 33cl",
        "description": "Coca Cola lattina 33cl",
        "price": 2.50,
        "quantity": 120,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "5449000054227",
        "name": "Coca Cola Zero 33cl",
        "description": "Coca Cola Zero lattina 33cl",
        "price": 2.50,
        "quantity": 80,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "5449000000439",
        "name": "Fanta 33cl",
        "description": "Fanta arancia lattina 33cl",
        "price": 2.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "5449000000453",
        "name": "Sprite 33cl",
        "description": "Sprite lattina 33cl",
        "price": 2.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8000430133714",
        "name": "Acqua Naturale San Benedetto 1L",
        "description": "Acqua minerale naturale San Benedetto 1 litro",
        "price": 1.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8000430133721",
        "name": "Acqua Frizzante San Benedetto 1L",
        "description": "Acqua minerale frizzante San Benedetto 1 litro",
        "price": 1.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8000755014907",
        "name": "Birra Moretti 33cl",
        "description": "Birra Moretti bottiglia 33cl",
        "price": 3.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8000755001808",
        "name": "Birra Peroni 33cl",
        "description": "Birra Peroni bottiglia 33cl",
        "price": 3.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8000300282017",
        "name": "Chinotto Lurisia 27.5cl",
        "description": "Chinotto Lurisia bottiglia 27.5cl",
        "price": 3.00,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8002270002106",
        "name": "Aranciata San Pellegrino 33cl",
        "description": "Aranciata San Pellegrino lattina 33cl",
        "price": 2.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    {
        "ean": "8002270002113",
        "name": "Limonata San Pellegrino 33cl",
        "description": "Limonata San Pellegrino lattina 33cl",
        "price": 2.50,
        "quantity": 50,
        "category": "Bevande",
        "image_url": None
    },
    
    # Prodotti secchi (Dry goods)
    {
        "ean": "8076809513378",
        "name": "Spaghetti Barilla 500g",
        "description": "Spaghetti n.5 Barilla 500g",
        "price": 1.20,
        "quantity": 50,
        "category": "Pasta",
        "image_url": None
    },
    {
        "ean": "8076809513385",
        "name": "Penne Rigate Barilla 500g",
        "description": "Penne Rigate Barilla 500g",
        "price": 1.20,
        "quantity": 50,
        "category": "Pasta",
        "image_url": None
    },
    {
        "ean": "8076809513392",
        "name": "Fusilli Barilla 500g",
        "description": "Fusilli Barilla 500g",
        "price": 1.20,
        "quantity": 50,
        "category": "Pasta",
        "image_url": None
    },
    {
        "ean": "8076809532839",
        "name": "Farfalle Barilla 500g",
        "description": "Farfalle Barilla 500g",
        "price": 1.20,
        "quantity": 50,
        "category": "Pasta",
        "image_url": None
    },
    {
        "ean": "8001440204913",
        "name": "Riso Arborio Gallo 1kg",
        "description": "Riso Arborio per risotti Gallo 1kg",
        "price": 3.50,
        "quantity": 50,
        "category": "Riso",
        "image_url": None
    },
    {
        "ean": "8001440101366",
        "name": "Riso Carnaroli Gallo 1kg",
        "description": "Riso Carnaroli per risotti Gallo 1kg",
        "price": 4.50,
        "quantity": 50,
        "category": "Riso",
        "image_url": None
    },
    
    # Conserve e salse (Canned goods and sauces)
    {
        "ean": "8076800195057",
        "name": "Pomodoro Pelato Mutti 400g",
        "description": "Pomodoro pelato italiano Mutti 400g",
        "price": 1.50,
        "quantity": 50,
        "category": "Conserve",
        "image_url": None
    },
    {
        "ean": "8076800195385",
        "name": "Passata di Pomodoro Mutti 700g",
        "description": "Passata di pomodoro Mutti 700g",
        "price": 1.80,
        "quantity": 50,
        "category": "Conserve",
        "image_url": None
    },
    {
        "ean": "8076809513422",
        "name": "Sugo Basilico Barilla 400g",
        "description": "Sugo al basilico Barilla 400g",
        "price": 2.20,
        "quantity": 50,
        "category": "Salse",
        "image_url": None
    },
    {
        "ean": "8076809513439",
        "name": "Pesto alla Genovese Barilla 190g",
        "description": "Pesto alla genovese Barilla 190g",
        "price": 3.50,
        "quantity": 50,
        "category": "Salse",
        "image_url": None
    },
    {
        "ean": "8005510001082",
        "name": "Olio Extra Vergine d'Oliva Monini 750ml",
        "description": "Olio extra vergine d'oliva Monini 750ml",
        "price": 8.50,
        "quantity": 50,
        "category": "Condimenti",
        "image_url": None
    },
    {
        "ean": "8008440079651",
        "name": "Aceto Balsamico di Modena Ponti 500ml",
        "description": "Aceto balsamico di Modena IGP Ponti 500ml",
        "price": 4.50,
        "quantity": 50,
        "category": "Condimenti",
        "image_url": None
    },
    
    # Formaggi (Cheeses)
    {
        "ean": "8002580001028",
        "name": "Parmigiano Reggiano DOP 200g",
        "description": "Parmigiano Reggiano DOP grattugiato 200g",
        "price": 5.50,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    {
        "ean": "8002580001035",
        "name": "Grana Padano DOP 200g",
        "description": "Grana Padano DOP grattugiato 200g",
        "price": 4.80,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    {
        "ean": "8000700000122",
        "name": "Mozzarella di Bufala DOP 250g",
        "description": "Mozzarella di bufala campana DOP 250g",
        "price": 4.50,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    {
        "ean": "8000700000139",
        "name": "Mozzarella Fior di Latte 250g",
        "description": "Mozzarella fior di latte 250g",
        "price": 2.50,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    {
        "ean": "8002580002018",
        "name": "Pecorino Romano DOP 200g",
        "description": "Pecorino Romano DOP grattugiato 200g",
        "price": 5.00,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    {
        "ean": "8000300282024",
        "name": "Mascarpone 250g",
        "description": "Mascarpone 250g",
        "price": 3.20,
        "quantity": 50,
        "category": "Formaggi",
        "image_url": None
    },
    
    # Salumi (Cured meats)
    {
        "ean": "8002960014401",
        "name": "Prosciutto Crudo di Parma DOP 100g",
        "description": "Prosciutto crudo di Parma DOP affettato 100g",
        "price": 6.50,
        "quantity": 50,
        "category": "Salumi",
        "image_url": None
    },
    {
        "ean": "8002960014418",
        "name": "Prosciutto Cotto Alta Qualità 100g",
        "description": "Prosciutto cotto alta qualità affettato 100g",
        "price": 3.50,
        "quantity": 50,
        "category": "Salumi",
        "image_url": None
    },
    {
        "ean": "8002960014425",
        "name": "Salame Napoli 100g",
        "description": "Salame Napoli affettato 100g",
        "price": 4.00,
        "quantity": 50,
        "category": "Salumi",
        "image_url": None
    },
    {
        "ean": "8002960014432",
        "name": "Speck Alto Adige IGP 100g",
        "description": "Speck Alto Adige IGP affettato 100g",
        "price": 5.50,
        "quantity": 50,
        "category": "Salumi",
        "image_url": None
    },
    {
        "ean": "8002960014449",
        "name": "Mortadella Bologna IGP 100g",
        "description": "Mortadella Bologna IGP affettata 100g",
        "price": 3.00,
        "quantity": 50,
        "category": "Salumi",
        "image_url": None
    },
    
    # Farine e lieviti (Flours and yeast)
    {
        "ean": "8001100004016",
        "name": "Farina 00 per Pizza 1kg",
        "description": "Farina di grano tenero tipo 00 per pizza 1kg",
        "price": 1.20,
        "quantity": 50,
        "category": "Farine",
        "image_url": None
    },
    {
        "ean": "8001100004023",
        "name": "Farina Manitoba 1kg",
        "description": "Farina Manitoba per lievitati 1kg",
        "price": 2.50,
        "quantity": 50,
        "category": "Farine",
        "image_url": None
    },
    {
        "ean": "8001100004030",
        "name": "Semola Rimacinata 1kg",
        "description": "Semola rimacinata di grano duro 1kg",
        "price": 1.80,
        "quantity": 50,
        "category": "Farine",
        "image_url": None
    },
    {
        "ean": "8002780000019",
        "name": "Lievito di Birra Fresco 25g",
        "description": "Lievito di birra fresco 25g",
        "price": 0.30,
        "quantity": 50,
        "category": "Lieviti",
        "image_url": None
    },
    {
        "ean": "8000300030016",
        "name": "Lievito Istantaneo per Dolci 16g",
        "description": "Lievito istantaneo per dolci Pane degli Angeli 16g",
        "price": 0.80,
        "quantity": 50,
        "category": "Lieviti",
        "image_url": None
    },
    
    # Altri ingredienti (Other ingredients)
    {
        "ean": "8076800195408",
        "name": "Concentrato di Pomodoro Mutti 200g",
        "description": "Concentrato di pomodoro Mutti doppio concentrato 200g",
        "price": 1.50,
        "quantity": 50,
        "category": "Conserve",
        "image_url": None
    },
    {
        "ean": "8000300030023",
        "name": "Sale Fino 1kg",
        "description": "Sale fino da cucina 1kg",
        "price": 0.50,
        "quantity": 50,
        "category": "Condimenti",
        "image_url": None
    },
    {
        "ean": "8000300030030",
        "name": "Sale Grosso 1kg",
        "description": "Sale grosso da cucina 1kg",
        "price": 0.50,
        "quantity": 50,
        "category": "Condimenti",
        "image_url": None
    },
    {
        "ean": "8001110000016",
        "name": "Zucchero Semolato 1kg",
        "description": "Zucchero semolato 1kg",
        "price": 1.20,
        "quantity": 50,
        "category": "Dolci",
        "image_url": None
    },
    {
        "ean": "8002580003015",
        "name": "Uova Fresche Categoria A 6 pezzi",
        "description": "Uova fresche di gallina categoria A, confezione da 6",
        "price": 2.50,
        "quantity": 50,
        "category": "Freschi",
        "image_url": None
    },
    {
        "ean": "8000700000146",
        "name": "Burro 250g",
        "description": "Burro di prima qualità 250g",
        "price": 2.80,
        "quantity": 50,
        "category": "Latticini",
        "image_url": None
    },
    {
        "ean": "8000300030047",
        "name": "Panna da Cucina 200ml",
        "description": "Panna fresca da cucina 200ml",
        "price": 1.50,
        "quantity": 50,
        "category": "Latticini",
        "image_url": None
    },
    {
        "ean": "8001110000023",
        "name": "Caffè Espresso Macinato 250g",
        "description": "Caffè espresso macinato moka 250g",
        "price": 4.50,
        "quantity": 50,
        "category": "Caffè",
        "image_url": None
    },
    {
        "ean": "8001110000030",
        "name": "Caffè in Grani 1kg",
        "description": "Caffè in grani per macchina espresso 1kg",
        "price": 15.00,
        "quantity": 50,
        "category": "Caffè",
        "image_url": None
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


def create_product(token, product):
    """Create a single inventory product"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"  → POST {API_URL}/inventory/")
    print(f"  → Product: {product['name']} (EAN: {product['ean']})")
    
    response = requests.post(
        f"{API_URL}/inventory/",
        json=product,
        headers=headers,
        allow_redirects=False
    )
    
    print(f"  ← Status: {response.status_code}")
    
    if response.status_code == 201:
        return True, response.json()
    elif response.status_code == 409:
        return False, "Product with this EAN already exists (skipping)"
    else:
        print(f"  ← Response: {response.text[:200]}")
        return False, f"Status {response.status_code}: {response.text}"


def main():
    print("=" * 60)
    print("RistoSmart - Inventory Population Script")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Total products to create: {len(INVENTORY_PRODUCTS)}")
    print("=" * 60)
    
    # Login
    token = login()
    
    # Create inventory products
    print(f"\nCreating {len(INVENTORY_PRODUCTS)} inventory products...")
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, product in enumerate(INVENTORY_PRODUCTS, 1):
        success, result = create_product(token, product)
        
        if success:
            print(f"✓ [{idx}/{len(INVENTORY_PRODUCTS)}] Created: {product['name']}")
            success_count += 1
        elif "already exists" in str(result):
            print(f"⊘ [{idx}/{len(INVENTORY_PRODUCTS)}] Skipped: {product['name']} (already exists)")
            skipped_count += 1
        else:
            print(f"✗ [{idx}/{len(INVENTORY_PRODUCTS)}] Failed: {product['name']}")
            print(f"  Error: {result}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully created: {success_count}")
    print(f"⊘ Skipped (already exist): {skipped_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"Total processed: {len(INVENTORY_PRODUCTS)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
