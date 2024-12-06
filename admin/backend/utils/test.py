from pymongo import MongoClient
from collections import Counter

# Configuración de la conexión
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']

def obtener_top_30_productos():
    # Recuperar todos los pedidos y extraer los SKUs
    orders = orders_collection.find({}, {'products.sku': 1})
    skus = [product['sku'] for order in orders for product in order.get('products', [])]

    # Contar la frecuencia de cada SKU
    sku_counter = Counter(skus)

    # Obtener los 30 productos más vendidos
    top_30 = sku_counter.most_common(30)

    # Formatear los resultados
    top_30_formatted = [{'sku': sku, 'cantidad': count} for sku, count in top_30]
    return top_30_formatted

if __name__ == '__main__':
    top_30_productos = obtener_top_30_productos()
    print("Los 30 productos más vendidos son:")
    for producto in top_30_productos:
        print(producto['sku'])
