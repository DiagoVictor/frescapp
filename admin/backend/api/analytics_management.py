
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
inventory_collection = db['inventory']

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
        "$lookup": {
            "from": "products_history",  # Colección a unir
            "let": {
                "child": "$product_info.child",  # Campo `child` de `products`
                "delivery_date": "$delivery_date"  # Campo `delivery_date` de `orders`
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                { "$eq": ["$child", "$$child"] },  # Unir por `child`
                                { "$eq": ["$operation_date", "$$delivery_date"] }  # Unir por `date`
                            ]
                        }
                    }
                }
            ],
            "as": "product_history_info"  # Nombre del campo donde se almacenará la información del historial del producto
        }
    },
    {
        "$unwind": {
            "path": "$product_history_info",
            "preserveNullAndEmptyArrays": True  # Permite que no haya coincidencias en `product_history`
        }
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
            "name_root": "$product_info.name",
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
            },
            "price_purchase_real": "$product_history_info.last_price_purchased"
        }
    }
]
    orders_data = list(orders_collection.aggregate(pipeline))
    orders_data_json = json.loads(json_util.dumps(orders_data))
    return jsonify(orders_data_json)

@analytics_api.route('/products_consolidated', methods=['GET'])
def get_products_consolidated():
    # Definir el rango de fechas
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)
    pipeline = [
    {
        "$match": {
            "delivery_date": {
                "$gte": fecha_inicio.strftime('%Y-%m-%d'),  # Fecha de inicio (hace 30 días)
                "$lte": fecha_fin.strftime('%Y-%m-%d')     # Fecha de fin (hoy)
            }
        }
    },
    {
        "$unwind": "$products"
    },
    {
        "$lookup": {
            "from": "products",
            "localField": "products.sku",
            "foreignField": "sku",
            "as": "product_info"
        }
    },
    {
        "$unwind": "$product_info"
    },
    {
        "$lookup": {
            "from": "products",
            "localField": "product_info.child",
            "foreignField": "sku",
            "as": "child_product_info"
        }
    },
    {
        "$unwind": {
            "path": "$child_product_info",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$lookup": {
            "from": "purchases",
            "let": { "sku": "$child_product_info.sku", "delivery_date": "$delivery_date" },
            "pipeline": [
                { "$unwind": "$products" },  # Desenrollar el array de productos en purchase
                { "$match":
                    { "$expr":
                        { "$and":
                            [
                                { "$eq": [ "$products.sku", "$$sku" ] },  # Comparar SKU
                                { "$eq": [ "$date", "$$delivery_date" ] }  # Comparar fecha
                            ]
                        }
                    }
                }
            ],
            "as": "purchase_info"
        }
    },
    {
        "$lookup": {
            "from": "inventory",
            "let": { "sku": "$child_product_info.sku", "delivery_date": "$delivery_date" },
            "pipeline": [
                { "$unwind": "$products" }, 
                { "$match":
                    { "$expr":
                        { "$and":
                            [
                                { "$eq": [ "$products.sku", "$$sku" ] },  # Comparar SKU
                                { "$eq": [ "$close_date", { "$dateToString": { "format": "%Y-%m-%d", "date": { "$dateSubtract": { "startDate": { "$toDate": "$$delivery_date" }, "unit": "day", "amount": 1 } } } } ] }
                            ]
                        }
                    }
                }
            ],
            "as": "inventory_info"
        }
    },
    {
        "$unwind": {
            "path": "$purchase_info",
            "preserveNullAndEmptyArrays": True  # Mantener documentos aunque no haya coincidencias
        }
    },
    {
        "$unwind": {
            "path": "$inventory_info",
            "preserveNullAndEmptyArrays": True  # Mantener documentos aunque no haya coincidencias
        }
    },
    {
        "$group": {
            "_id": {
                "fecha": "$delivery_date",
                "sku": "$child_product_info.sku"
            },
            "name": {"$first": "$child_product_info.name"},  # Nombre del child
            "categoria": {"$first": "$child_product_info.category"},
            "cantidad_vendida": {
                "$sum": {
                    "$multiply": ["$products.quantity", "$product_info.step_unit"]
                }
            },
            "cantidad_comprada": {
                "$first":  {
                    "$ifNull": ["$purchase_info.products.total_quantity", 0]
                }
            },
            "cantidad_inventario": {
                "$first": {
                     "$ifNull": ["$inventory_info.products.quantity",0]
                }
            },
            "precio_inventario": {
                "$first": {
                     "$ifNull": ["$inventory_info.products.cost",0]
                }
            },
            "precio_compra": {
                "$first": {
                    "$ifNull": ["$purchase_info.products.final_price_purchase", "$product_info.price_purchase"]
                }
            },
            "precio_venta": {
                "$avg": {
                    "$divide": ["$products.price_sale", "$product_info.step_unit"]  
                }
            },
            "lineas": {"$sum": 1}
        }
    },
    {
        "$project": {
            "_id": 0,  # Excluir el campo _id
            "fecha": "$_id.fecha",
            "sku": "$_id.sku",
            "name": 1,  # Nombre del child
            "categoria": 1,
            "cantidad_vendida": 1,
            "cantidad_comprada": 1,
            "cantidad_inventario": 1,
            "precio_inventario": 1,
            "precio_compra": 1,
            "precio_venta": 1,
            "lineas": 1
        }
    },
    {
        "$sort": {
            "fecha": 1  # Ordenar por fecha ascendente
        }
    }
]
    result = list(orders_collection.aggregate(pipeline))
    result_data_json = json.loads(json_util.dumps(result))
    return jsonify(result_data_json)