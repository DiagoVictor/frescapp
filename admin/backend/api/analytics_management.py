
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime, timedelta
from models.order import Order
from models.product import Product
import json
from bson import ObjectId, json_util


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
    # Definir el rango de fechas
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=120)

    # Convertir las fechas a objetos datetime para MongoDB
    fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
    # Pipeline de agregación
    pipeline = [
        {
            "$match": {
                "delivery_date": {
                    "$gte": fecha_inicio_str,
                    "$lte": fecha_fin_str
                }
            }
        },
        {
            "$unwind": "$products"  # Descomponer el array de productos
        },
        {
            "$lookup": {
                "from": "products",  # Colección a unir
                "localField": "products.child",  # Campo en `orders`
                "foreignField": "sku",  # Campo en `products`
                "as": "product_info"  # Nombre del campo donde se almacenará la información del producto
            }
        },
        {
            "$unwind": "$product_info"  # Descomponer el array resultante de `$lookup`
        },
        {
            "$project": {
                "order_number": 1,
                "customer_email": 1,
                "customer_phone": 1,
                "customer_document_number": "$customer_documentNumber",
                "customer_document_type": "$customer_documentType",
                "customer_name": 1,
                "delivery_date": 1,
                "status": 1,
                "created_at": 1,
                "updated_at": 1,
                "total": 1,
                "delivery_slot": "$deliverySlot",
                "payment_method": "$paymentMethod",
                "delivery_address": "$deliveryAddress",
                "delivery_address_details": "$deliveryAddressDetails",
                "sku": "$products.sku",
                "name": "$products.name",
                "name_root" :"$product_info.name",
                "quantity": "$products.quantity",
                "price_sale": "$products.price_sale",
                "price_purchase": "$product_info.price_purchase",
                "category": "$product_info.category",
                "root": "$product_info.root",
                "child": "$product_info.child",
                "discount": "$products.discount",
                "margen": "$product_info.margen",
                "iva": "$products.iva",
                "iva_value": "$products.iva_value",
                "step_unit": "$products.step_unit",
                "quantity_root": {
                    "$multiply": ["$products.quantity", "$products.step_unit"]
                }
            }
        }
    ]
    # Ejecutar la agregación
    orders_data = list(orders_collection.aggregate(pipeline))
    orders_data_json = json.loads(json_util.dumps(orders_data))
    return jsonify(orders_data_json)