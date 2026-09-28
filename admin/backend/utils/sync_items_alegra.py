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
    "authorization": "Basic ZmVzY2FwcEBnbWFpbC5jb206ZTMxNWIyOTQ2YjY4ZDk0NjExYjA=",
    "content-type": "application/json"
}

# Bodega "Principal" de la cuenta Alegra actual (fescapp@gmail.com)
ALEGRA_WAREHOUSE_ID = "019e8675-7063-73bd-8c98-7e69cea7dab8"

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

def find_item_by_reference(items, reference):
    return next((item for item in items if item.get("reference") == reference), None)

def _map_unit(unit):
    if unit == 'KG':
        return 'kilogram'
    elif unit == 'UND':
        return 'unit'
    return 'unit'  # Valor por defecto si no coincide

def _build_inventory(product):
    quantity = product.get("quantity") or 0
    return {
        "unit": _map_unit(product['unit']),
        "unitCost": product.get("price_purchase") or 0,
        "initialQuantity": quantity,
        "warehouses": [{"id": ALEGRA_WAREHOUSE_ID, "initialQuantity": quantity}]
    }

# Función para crear un producto en la API de Alegra
def create_item_in_alegra(product):
    payload = {
        "type": "product",
        "name": product["name"],
        "reference": product["sku"],
        "price": product["price_sale"],
        "inventory": _build_inventory(product)
    }

    response = requests.post(url_items, headers=headers, json=payload, timeout=30)
    if response.status_code == 201:
        print(f"Producto creado exitosamente: {response.json()}")
    else:
        print(f"Error al crear el producto: {response.status_code} - {response.text}")

def update_item_alegra(product):
    payload = {
        "type": "product",
        "name": product["name"],
        "reference": product["sku"],
        "price": product["price_sale"],
        "inventory": _build_inventory(product)
    }

    response = requests.put(url_items + '/' + str(product["id"]), headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        print(f"Producto actualizado exitosamente: {response.json()}")
    else:
        print(f"Error al actualizar el producto: {response.status_code} - {response.text}")


def sync_products():
    # Obtener todos los productos de la API de Alegra
    alegra_items = get_all_items()
    alegra_references = {item["reference"] for item in alegra_items}

    # Obtener todos los productos de la base de datos
    db_products = products_collection.find()
    for product in db_products:
        if product["sku"] not in alegra_references:
            print(f"Creando producto: {product['name']} ({product['sku']})")
            create_item_in_alegra(product)
        else:
            alegra_product = find_item_by_reference(alegra_items, product['sku'])
            product["id"] = alegra_product["id"]
            update_item_alegra(product)
            print(f"El producto {product['name']} ({product['sku']}) actualizado en Alegra")

sync_products()
