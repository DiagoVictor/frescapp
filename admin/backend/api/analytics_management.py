from flask import Blueprint, jsonify, current_app, Response
from datetime import datetime, timedelta
import json
from bson import json_util
from ..models.order import Order
from ..models.product import Product

from ..db import get_db


analytics_api = Blueprint('analytics', __name__)


@analytics_api.route('/health')
def health_check():
    return "OK", 200


# ===========================================
# COSTOS DIARIOS
# ===========================================
@analytics_api.route('/costs', methods=['GET'])
def get_cost():
    from flask import current_app
    with current_app.app_context():
        db = get_db()
        routes_collection = db['routes']
        purchases_collection = db['purchases']
        orders_collection = db['orders']
        costs_collection = db['costs']
        inventory_collection = db['inventory']

        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=120)

        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

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
                    "cost_tech": 6250,
                    "cost_others": 0,
                    "wh_rent": 52080
                }

        # =============== PIPELINE COGS ===============
        pipeline = [
            {"$match": {"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}},
            {"$unwind": "$products"},
            {"$lookup": {"from": "products", "localField": "products.sku", "foreignField": "sku", "as": "product_info"}},
            {"$unwind": "$product_info"},
            {"$lookup": {"from": "products", "localField": "product_info.child", "foreignField": "sku", "as": "child_product_info"}},
            {"$unwind": {"path": "$child_product_info", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "purchases",
                    "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
                    "pipeline": [
                        {"$unwind": "$products"},
                        {"$match": {"$expr": {"$and": [{"$eq": ["$products.sku", "$$sku"]}, {"$eq": ["$date", "$$delivery_date"]}]}}}
                    ],
                    "as": "purchase_info"
                }
            },
            {
                "$lookup": {
                    "from": "inventory",
                    "let": {"sku": "$child_product_info.sku", "delivery_date": "$delivery_date"},
                    "pipeline": [
                        {"$unwind": "$products"},
                        {"$match": {"$expr": {"$and": [
                            {"$eq": ["$products.sku", "$$sku"]},
                            {"$eq": ["$close_date", {"$dateToString": {"format": "%Y-%m-%d", "date": {"$dateSubtract": {"startDate": {"$toDate": "$$delivery_date"}, "unit": "day", "amount": 1}}}}]}
                        ]}}}
                    ],
                    "as": "inventory_info"
                }
            },
            {"$unwind": {"path": "$purchase_info", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$inventory_info", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": {"fecha": "$delivery_date", "sku": "$child_product_info.sku"},
                "cantidad_vendida": {"$sum": {"$multiply": ["$products.quantity", "$product_info.step_unit"]}},
                "cantidad_inventario": {"$first": {"$ifNull": ["$inventory_info.products.quantity", 0]}},
                "precio_inventario": {"$first": {"$ifNull": ["$inventory_info.products.cost", 0]}},
                "precio_compra": {"$first": {"$ifNull": ["$purchase_info.products.final_price_purchase", "$product_info.price_purchase"]}}
            }},
            {"$addFields": {
                "costo_total": {
                    "$cond": [
                        {"$gte": ["$cantidad_inventario", "$cantidad_vendida"]},
                        {"$multiply": ["$cantidad_vendida", "$precio_inventario"]},
                        {
                            "$add": [
                                {"$multiply": ["$cantidad_inventario", "$precio_inventario"]},
                                {"$multiply": [{"$subtract": ["$cantidad_vendida", "$cantidad_inventario"]}, "$precio_compra"]}
                            ]
                        }
                    ]
                }
            }},
            {"$group": {"_id": "$_id.fecha", "cogs": {"$sum": "$costo_total"}}}
        ]

        cogs_por_dia = orders_collection.aggregate(pipeline)

        for item in cogs_por_dia:
            fecha = item["_id"]
            initialize_daily_summary(fecha)
            daily_summary[fecha]["cogs"] += item["cogs"]

        # ===== COSTOS LOGÍSTICOS =====
        rutas = routes_collection.find({"close_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}, {"close_date": 1, "cost": 1})
        for ruta in rutas:
            fecha = ruta.get('close_date')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            daily_summary[fecha]["logistics_cost"] += ruta.get('cost', 0)

        # ===== ORDENES Y GMV =====
        ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}, {"delivery_date": 1, "products": 1})
        for orden in ordenes:
            fecha = orden.get('delivery_date')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            daily_summary[fecha]["total_orders"] += 1
            for producto in orden.get('products', []):
                daily_summary[fecha]["total_lines"] += 1
                daily_summary[fecha]["gmv"] += producto.get('price_sale', 0) * producto.get('quantity', 0)

        # ===== COSTOS ADICIONALES =====
        costs = costs_collection.find({"typePeriod": "Diario"}, {"period": 1, "typeCost": 1, "amount": 1})
        for cost in costs:
            fecha = cost.get('period')
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            initialize_daily_summary(fecha)
            tipo_costo = cost.get('typeCost')
            if tipo_costo in daily_summary[fecha]:
                daily_summary[fecha][tipo_costo] += cost.get('amount', 0)

        # ===== RESULTADO FINAL =====
        result = []
        for fecha, data in daily_summary.items():
            for var in ["wh_rent", "logistics_cost", "cogs", "gmv", "total_orders", "total_lines", "cost_tech", "cost_others"]:
                result.append({
                    "fecha": fecha,
                    "variable": var,
                    "valor": float(data[var]) if isinstance(data[var], (int, float)) else 0
                })

        return jsonify(result), 200


# ===========================================
# ÓRDENES Y PRODUCTOS CONSOLIDADOS
# ===========================================
@analytics_api.route('/orders', methods=['GET'])
def get_orders():
    with current_app.app_context():
        db = get_db()
        orders_collection = db['orders']

        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=120)
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

        pipeline = [
            {"$match": {"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}},
            {"$unwind": "$products"},
            {"$lookup": {"from": "products", "localField": "products.child", "foreignField": "sku", "as": "product_info"}},
            {"$unwind": "$product_info"},
            {"$project": {
                "order_number": 1,
                "delivery_date": 1,
                "status": 1,
                "products": 1,
                "product_info": 1
            }}
        ]

        orders_data = list(orders_collection.aggregate(pipeline))
        return Response(json_util.dumps(orders_data), mimetype='application/json'), 200

@analytics_api.route('/ue_daily/', methods=['GET'])
def ue_daily():
    db = get_db()
    orders_collection = db['orders']
    # Calcular las fechas de inicio y fin de los últimos 3 meses
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=60)

    # Convertir las fechas a formato de cadena para MongoDB
    fecha_inicio_str =  '2025-05-01'
    fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')

    # Variables de resumen agrupadas por día
    daily_summary = {}

    def initialize_daily_summary(fecha):
        if fecha not in daily_summary:
            daily_summary[fecha] = {
                "date": fecha,
                "logistics_cost": 0,
                "cogs": 0,  # COGS (Costo de los Bienes Vendidos)
                "gmv": 0,
                "total_orders": 0,
                "total_lines": 0,
                "cost_tech": 0,
                "cost_others": 0,
                "wh_rent": 0,
                "perssonel": 0,
                "cost_supply": 0,
                "detalle": "",
                "total_orders": 0,
                "total_lines": 0
            }

    # Pipeline para calcular el costo total de los productos vendidos por día
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
                    { "$unwind": "$products" },
                    { "$match":
                        { "$expr":
                            { "$and":
                                [
                                    { "$eq": [ "$products.sku", "$$sku" ] },
                                    { "$eq": [ "$date", "$$delivery_date" ] }
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
                                    { "$eq": [ "$products.sku", "$$sku" ] },
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
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$unwind": {
                "path": "$inventory_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$group": {
                "_id": {
                    "fecha": "$delivery_date",
                    "sku": "$child_product_info.sku"
                },
                "cantidad_vendida": {
                    "$sum": {
                        "$multiply": ["$products.quantity", "$product_info.step_unit"]
                    }
                },
                "cantidad_inventario": {
                    "$first": {
                        "$ifNull": ["$inventory_info.products.quantity", 0]
                    }
                },
                "precio_inventario": {
                    "$first": {
                        "$ifNull": ["$inventory_info.products.cost", 0]
                    }
                },
                "precio_compra": {
                    "$first": {
                        "$ifNull": ["$purchase_info.products.final_price_purchase",0]
                    }
                }
            }
        },
        {
            "$addFields": {
                "costo_total": {
                    "$cond": [
                        { "$gte": ["$cantidad_inventario", "$cantidad_vendida"] },
                        { "$multiply": ["$cantidad_vendida", "$precio_inventario"] },
                        {
                            "$add": [
                                { "$multiply": ["$cantidad_inventario", "$precio_inventario"] },
                                { "$multiply": [
                                    { "$subtract": ["$cantidad_vendida", "$cantidad_inventario"] },
                                    "$precio_compra"
                                ]}
                            ]
                        }
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$_id.fecha",
                "cogs": { "$sum": "$costo_total" }  # Sumar el costo total por día
            }
        }
    ]

    # Ejecutar el pipeline para obtener el COGS por día
    cogs_por_dia = db.orders.aggregate(pipeline)

    # Procesar los resultados del pipeline y actualizar el daily_summary
    for item in cogs_por_dia:
        fecha = item["_id"]
        initialize_daily_summary(fecha)
        daily_summary[fecha]["cogs"] += item["cogs"]

    # Procesar rutas para costos logísticos
    rutas = db.routes.find({"close_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}, {"close_date": 1, "cost": 1})
    for ruta in rutas:
        fecha = ruta.get('close_date')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        daily_summary[fecha]["logistics_cost"] += ruta.get('cost', 0)

    # Procesar órdenes para GMV, órdenes, líneas y clientes
    ordenes = db.orders.find({"delivery_date": {"$gte": fecha_inicio_str, "$lte": fecha_fin_str}}, {"delivery_date": 1, "products": 1})
    for orden in ordenes:
        fecha = orden.get('delivery_date')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        daily_summary[fecha]["total_orders"] += 1


        for producto in orden.get('products', []):
            daily_summary[fecha]["total_lines"] += 1
            daily_summary[fecha]["gmv"] += producto.get('price_sale', 0) * producto.get('quantity', 0)
    # Procesar costos adicionales de la colección 'costs'
    costs = db.costs.find({"typePeriod": "Diario",     "period": { "$gt": fecha_inicio_str }}, {"period": 1, "typeCost": 1, "amount": 1, "detail": 1})
    for cost in costs:
        fecha = cost.get('period')
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')

        initialize_daily_summary(fecha)
        tipo_costo = cost.get('typeCost')
        if tipo_costo in daily_summary[fecha]:
            daily_summary[fecha][tipo_costo] += cost.get('amount', 0)
            daily_summary[fecha]["detalle"] += cost.get('detail', '')

    # Construir el resultado final con la estructura deseada
    result = []
    for fecha, data in daily_summary.items():
        # Agregar el costo de renta de almacén como 'warehouse'
        result.append({
            "fecha": fecha,
            "variable": "warehouse",
            "valor": -float(data["wh_rent"]),
            "detalle" : "Renta de almacén"
        })
        
        # Agregar otros costos si es necesario
        result.append({
            "fecha": fecha,
            "variable": "logistics_cost",
            "valor": -float(data["logistics_cost"]),
            "detalle": "Costos logísticos"
        })
        
        # Agregar COGS
        result.append({
            "fecha": fecha,
            "variable": "cogs",
            "valor": -float(data["cogs"]),
            "detalle": "Costo de bienes vendidos"
        })
        result.append({
            "fecha": fecha,
            "variable": "gmv",
            "valor": float(data["gmv"]),
            "detalle": "Valor bruto de mercancía"
        })
        result.append({
            "fecha": fecha,
            "variable": "cost_tech",
            "valor": -float(data["cost_tech"]),
            "detalle": "Costos tecnológicos"
        })
        result.append({
            "fecha": fecha,
            "variable": "cost_others",
            "valor": -float(data["cost_others"]),
            "detalle": data["detalle"]
        })
        result.append({
            "fecha": fecha,
            "variable": "perssonel",
            "valor": -float(data["perssonel"]),
            "detalle": "Costos de personal"
        })
        result.append({
            "fecha": fecha,
            "variable": "cost_supply",
            "valor": -float(data["cost_supply"]),
            "detalle": "Costos de suministros"
        })
        result.append({
            "fecha": fecha,
            "variable": "total_orders",
            "valor": float(data["total_orders"]),
            "detalle": "Total de órdenes"
        })
        result.append({
            "fecha": fecha,
            "variable": "total_lines",
            "valor": float(data["total_lines"]),
            "detalle": "Total de líneas"
        })
    return jsonify(result), 200
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
    result = list(orders.aggregate(pipeline))
    return Response(json_util.dumps(result), mimetype='application/json')