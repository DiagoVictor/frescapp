import requests
from pymongo import MongoClient

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
products_collection = db['products']  # Suponiendo que los productos están en esta colección

# URL base y cabeceras para la API de Alegra
url_items = "https://api.alegra.com/api/v1/items"
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0",
    "content-type": "application/json"
}

# Función para obtener todos los productos de Alegra
def get_all_items():
    items = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            items.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de productos: {response.status_code} - {response.text}")
            break
    return items

# Función para crear un producto en la API de Alegra
def create_item_in_alegra(product):
    payload = {
        "name": product["name"],
        "reference": product["sku"],
        "price": product["price_sale"]
    }
    response = requests.post(url_items, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Producto creado exitosamente: {response.json()}")
    else:
        print(f"Error al crear el producto: {response.status_code} - {response.text}")

# Función principal
def sync_products():
    # Obtener todos los productos de la API de Alegra
    alegra_items = get_all_items()
    alegra_references = {item["reference"] for item in alegra_items}

    # Obtener todos los productos de la base de datos
    db_products = products_collection.find()

    for product in db_products:
        # Verificar si el producto ya existe en Alegra usando la referencia (sku)
        if product["sku"] not in alegra_references:
            # Si no existe, crear el producto en Alegra
            print(f"Creando producto: {product['name']} ({product['sku']})")
            create_item_in_alegra(product)
        else:
            print(f"El producto {product['name']} ({product['sku']}) ya existe en Alegra")

# Ejecutar la sincronización de productos
sync_products()
