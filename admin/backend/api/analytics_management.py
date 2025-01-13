
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timedelta
from models.order import Order
from models.product import Product


analytics_api = Blueprint('analytics', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
routes_collection = db['routes']
purchases_collection = db['purchases']
orders_collection = db['orders']
costs_collection = db['costs']

@analytics_api.route('/health')
def health_check():
    return "OK", 200
@analytics_api.route('/costs', methods=['GET'])
def gest_cost():
    # Calcular las fechas de inicio y fin de los últimos 3 meses
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=120)

    # Convertir las fechas a formato de cadena para MongoDB
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # Variables de resumen agrupadas por día
    daily_summary = {}

    def initialize_daily_summary(fecha):
        if fecha not in daily_summary:
            daily_summary[fecha] = {
                "date": fecha,
                "logistics_cost": 0,
                "cogs": 0,
                "gmv": 0,
                "total_orders": 0,
                "total_lines": 0,
                "unique_clients": set(),
                "cost_tech": 0,
                "cost_others": 0,
                "wh_rent": 0,
                "sales_force": 0
            }

    # Procesar rutas para costos logísticos
    rutas = routes_collection.find({"close_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}})
    for ruta in rutas:
        fecha = ruta.get('close_date')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        daily_summary[fecha]["logistics_cost"] += ruta.get('cost', 0)

    # Procesar compras para calcular COGS
    compras = purchases_collection.find({"date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}})
    for compra in compras:
        fecha = compra.get('date')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        for producto in compra.get('products', []):
            precio = producto.get('final_price_purchase')
            cantidad = producto.get('total_quantity_ordered')
            if precio is not None and cantidad is not None:
                daily_summary[fecha]["cogs"] += round(float(precio) * float(cantidad), 2)


    # Procesar órdenes para GMV, órdenes, líneas y clientes
    ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}})
    for orden in ordenes:
        fecha = orden.get('delivery_date')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        daily_summary[fecha]["total_orders"] += 1
        daily_summary[fecha]["unique_clients"].add(orden.get('customer_email'))
        for producto in orden.get('products', []):
            daily_summary[fecha]["total_lines"] += 1
            daily_summary[fecha]["gmv"] += producto.get('price_sale', 0) * producto.get('quantity', 0)

    # Procesar costos adicionales de la colección 'costs'
    costs = costs_collection.find({"typePeriod": "Diario"})
    for cost in costs:
        fecha = cost.get('period')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        tipo_costo = cost.get('typeCost')
        if tipo_costo in daily_summary[fecha]:
            daily_summary[fecha][tipo_costo] += cost.get('amount', 0)

    # Construir el resultado final
    result = []
    for fecha, data in daily_summary.items():
        data["unique_clients"] = len(data["unique_clients"])
        result.append(data)

    return jsonify(result), 200

@analytics_api.route('/orders', methods=['GET'])
def get_orders():
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=120)

    # Convertir las fechas a formato de cadena para MongoDB
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
    orders_cursor = Order.objects_date(fecha_inicio_str, fecha_fin_str)

    # Crear una lista para almacenar las órdenes duplicadas por producto
    orders_data = []

    for order in orders_cursor:
        # Información general de la orden
        base_order_data = {
            "order_id": str(order["_id"]),
            "order_number": order.get("order_number", order.get("orderNumber", "N/A")),
            "customer_email": order.get("customer_email", order.get("customerEmail", "N/A")),
            "customer_phone": order.get("customer_phone", order.get("customerPhone", "N/A")),
            "customer_document_number": order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A")),
            "customer_document_type": order.get("customer_documentType", order.get("customerDocumentType", "N/A")),
            "customer_name": order.get("customer_name", order.get("customerName", "N/A")),
            "delivery_date": order.get("delivery_date", order.get("deliveryDate", "N/A")),
            "status": order.get("status", "N/A"),
            "created_at": order.get("created_at", "N/A"),
            "updated_at": order.get("updated_at", "N/A"),
            "total": order.get("total", 0),
            "delivery_slot": order.get("deliverySlot", "N/A"),
            "payment_method": order.get("paymentMethod", "N/A"),
            "delivery_address": order.get("deliveryAddress", "N/A"),
            "delivery_address_details": order.get("deliveryAddressDetails", "N/A")
        }

        # Crear un documento por cada producto en la orden
        for product in order.get("products", []):
            product_data = {
                "sku": product.get("sku", ""),
                "name": product.get("name", "Unknown"),
                "quantity": product.get("quantity", 0),
                "price_sale": product.get("price_sale", 0),
                "price_purchase": product.get("price_purchase", "N/A"),
                "category": product.get("category", "N/A"),
                "root": product.get("root", "N/A"),
                "child": product.get("child", "N/A"),
                "discount": product.get("discount", "N/A"),
                "margen": product.get("margen", "N/A"),
                "iva": product.get("iva", "N/A"),
                "iva_value": product.get("iva_value", "N/A"),
                "step_unit": product.get("step_unit", "N/A")            
            }

            # Combinar la información de la orden con la del producto
            combined_data = {**base_order_data, **product_data}
            orders_data.append(combined_data)

    # Retornar los datos en formato JSON
    return jsonify(orders_data)
