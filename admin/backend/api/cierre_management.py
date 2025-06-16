from flask import Blueprint, jsonify, request
from models.cierre import Cierre  # Importa la clase Cierre desde el archivo de modelos
from pymongo import MongoClient
from datetime import datetime
from bson import json_util, ObjectId
from models.route import Route
from models.inventory import Inventory
from models.purchase import Purchase
from models.cost import Cost
from models.order import Order
from datetime import datetime, timedelta
import api.alegra_management as alegra_api
import api.route_management as route_api
import api.purchase_management as purchase_api
import api.inventory_management as inventory_api
import api.ue_management as ue_api
import time
# Configuración de Flask Blueprint
cierres_api = Blueprint('cierres', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
purchases_collection = db['purchases']
routes_collection = db['routes']
costs_collection = db["costs"]
cierres_collection = db['cierres']

def func_create_cierre(fecha_in):
    pipeline_cog = [
        {
            "$match": {
                "delivery_date": {
                    "$gte": fecha_in,
                    "$lte": fecha_in
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
    inventario_hoy = Inventory.total_by_date(fecha_in)
    fecha_ayer = (datetime.strptime(fecha_in, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    inventario_ayer = Inventory.total_by_date(fecha_ayer)
    purchase_value = Purchase.total_by_date(fecha_in)
    cogs = db.orders.aggregate(pipeline_cog)
    doc = next(cogs, None)
    if doc:
        cogs = doc['cogs'] if doc['cogs'] else 0
    else:
        cogs = 0
    clientes = set()
    gmv = 0
    total_ordenes = 0
    total_lineas = 0
    ordenes = orders_collection.find({"delivery_date": {"$gte": fecha_in, "$lte": fecha_in}})
    for orden in ordenes:
        total_ordenes += 1
        clientes.add(orden['customer_email'])
        for producto in orden['products']:
            quantity = producto['quantity']
            total_lineas = total_lineas + 1
            gmv += producto['price_sale'] * quantity
    aov = round(gmv / total_ordenes, 2) if total_ordenes > 0 else 0
    alv = round(gmv / total_lineas, 2) if total_lineas > 0 else 0
    cartera_total = 0
    efectivo = 0
    davivienda = 0
    bancolombia = 0
    cartera = 0
    orders_with_cartera = Order.find_by_status("Pendiente de pago")
    for order in orders_with_cartera:
        cartera_total += int(order.get("total"))
    ruta = Route.find_by_date(fecha_in)
    stops = ruta.stops
    cost_log = ruta.cost
    for stop in stops:
        if stop.get("payment_method") == "Davivienda" and stop.get("status") == "Pagada":
            davivienda = davivienda + (int(stop.get("total_charged")) or 0)
        if stop.get("payment_method") == "Bancolombia" and stop.get("status") == "Pagada":
            bancolombia = bancolombia + (int(stop.get("total_charged")) or 0)
        if stop.get("payment_method") == "Efectivo"  and stop.get("status") == "Pagada":
            efectivo = efectivo + (int(stop.get("total_charged")) or 0)
        if stop.get("status") != "Pagada":
            cartera = cartera + (int(stop.get("total_charged")) or 0)
    new_ue = {
        "close_date": fecha_in,
        "gmv": gmv,
        "cogs": cogs,
        "purchase" : purchase_value,
        "leakage": float(purchase_value) + float(inventario_ayer) - float(inventario_hoy) - float(cogs),
        "inventory" : inventario_hoy,
        "Net Profit": 0,
        "Gross Profit as % of GMV": 0,
        "Gross Profit": 0,
        "orders": total_ordenes,
        "lines": total_lineas,
        "aov": aov,
        "alv": alv,
        "cash_margin": round(gmv - cogs, 2),
        "margin": round((gmv - cogs) / gmv * 100, 2) if gmv > 0 else 0,
        "cartera_total": cartera_total,
        "cartera_today": cartera,
        "davivienda": davivienda,
        "bancolombia": bancolombia,
        "cash": efectivo,
        "cost_log": cost_log,
    }
    cierres_collection.insert_one(new_ue)
# Endpoint para listar todos los cierres
@cierres_api.route('/', methods=['GET'])
def list_cierres():
    cierres = Cierre.listar()
    return jsonify([
        {
            "id": str(item["_id"]),
            "close_date":    item.get("close_date"),
            "gmv":           item.get("gmv"),
            "cogs":          item.get("cogs"),
            "purchase":      item.get("purchase"),
            "leakage":       item.get("leakage"),
            "inventory":     item.get("inventory"),
            "orders":        item.get("orders"),
            "lines":         item.get("lines"),
            "aov":           item.get("aov"),
            "alv":           item.get("alv"),
            "cash_margin":   item.get("cash_margin"),
            "margin":        item.get("margin"),
            "cartera_total": item.get("cartera_total"),
            "cartera_today": item.get("cartera_today"),
            "davivienda":    item.get("davivienda"),
            "bancolombia":   item.get("bancolombia"),
            "cash":          item.get("cash"),
            "cost_log":      item.get("cost_log"),
        }
        for item in cierres
    ])


# Endpoint para obtener un cierre por ID
@cierres_api.route('/<fecha>/', methods=['GET'])
def get_cierre(fecha):
    try:
        cierre = Cierre.obtener_por_fecha(fecha)
        if cierre:
            return jsonify(json_util.dumps(cierre)), 200
        else:
            return jsonify({"error": "Cierre no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para crear un nuevo cierre
@cierres_api.route('/<fecha_in>', methods=['POST'])
def create_cierre(fecha_in):
    # Paso 1: Generar facturas de pedidos del dia en curso
    orders = Order.find_by_date(fecha_in,fecha_in)
    for order in orders:
        if order.get("alegra_id") == "000":
            alegra_api.func_send_invoice(order["order_number"])
            time.sleep(3)  
    
    # Paso 2: Generar DS de compras del dia en curso
    purchase = Purchase.get_by_date(fecha_in)
    if purchase:
        if purchase.status != "Facturada":
            alegra_api.func_send_purchase(fecha_in)

    # Paso 3: Cerrar la ruta
    # rutas = Route.find_by_date(fecha_in)
    # for ruta in rutas:
    #     ruta.close_route()
    
    # Paso 4: Crear la ruta del dia siguiente
    fecha_siguiente = (datetime.strptime(fecha_in, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    ruta = Route.find_by_date(fecha_siguiente)
    if ruta:
        ruta.delete_route()
    route_api.func_create_route(fecha_siguiente)
    orders = Order.find_by_date(fecha_siguiente,fecha_siguiente)
    for order in orders:
        order_to_update = Order.object(order.get("_id"))
        if order_to_update:
            order_to_update.status = "Ruteada"
            order_to_update.updated()
    
    # Paso 5: Crear la OC del dia siguiente
    purchase = Purchase.get_by_date(fecha_siguiente)
    if purchase:
        purchase.delete()
    purchase_api.func_create_purchase(fecha_siguiente)

    # Paso 6: Crear el inventario del dia siguiente
    inventory = Inventory.get_by_date(fecha_siguiente)
    if inventory:
        inventory.delete()
    inventory_api.func_create_inventory(fecha_siguiente)

    # Paso 7: Calcular los datos del cierre
    func_create_cierre(fecha_in)
    return jsonify({"message": "Cierre creado exitosamente"}), 201


# Endpoint para editar un cierre existente
@cierres_api.route('/<id>/', methods=['PUT'])
def update_cierre(id):
    try:
        data = request.get_json()
        cierre_editar = Cierre(
            id=id,
            fecha=data.get('fecha'),
            efectivo=data.get('efectivo'),
            davivienda=data.get('davivienda'),
            bancolombia=data.get('bancolombia'),
            cartera=data.get('cartera'),
            inventario_hoy=data.get('inventario_hoy'),
            inventario_ayer=data.get('inventario_ayer'),
            ruta=data.get('ruta'),
            aux_ops=data.get('aux_ops'),
            cogs=data.get('cogs'),
            cash_margin=data.get('cash_margin'),
            efectivo_total = data.get("efectivo_total"),
            davivienda_total = data.get("davivienda_total"),
            bancolombia_total = data.get("bancolombia_total"),
            cartera_total = data.get("cartera_total"),
            cierre_total = data.get("cierre_total"),
            deuda_total = data.get("deuda_total")
        )
        cierre_editar.editar()
        return jsonify({"message": "Cierre actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para eliminar un cierre
@cierres_api.route('/<id>/', methods=['DELETE'])
def delete_cierre(id):
    try:
        cierre_eliminar = Cierre(id=id)
        cierre_eliminar.eliminar()
        return jsonify({"message": "Cierre eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
