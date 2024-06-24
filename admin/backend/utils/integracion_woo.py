from woocommerce import API

# Configura tu API de WooCommerce
wcapi = API(
    url="https://tutienda.com",  # Reemplaza con la URL de tu tienda
    consumer_key="tu_consumer_key",  # Reemplaza con tu clave de consumidor
    consumer_secret="tu_consumer_secret",  # Reemplaza con tu secreto de consumidor
    version="wc/v3"  # Usa la versión 3 de la API de WooCommerce
)

# Obtén los pedidos
response = wcapi.get("orders")

# Verifica si la solicitud fue exitosa
if response.status_code == 200:
    pedidos = response.json()
    for pedido in pedidos:
        print(f"ID del pedido: {pedido['id']}")
        print(f"Fecha del pedido: {pedido['date_created']}")
        print(f"Estado del pedido: {pedido['status']}")
        print(f"Total del pedido: {pedido['total']}")
        print("-----")
else:
    print(f"Error {response.status_code}: {response.text}")
