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

# Configuración de Flask Blueprint
cierres_api = Blueprint('cierres', __name__)

# Endpoint para listar todos los cierres
@cierres_api.route('/', methods=['GET'])
def list_cierres():
    cierres = Cierre.listar()
    return jsonify([{
        "id": str(item["_id"]),
        "fecha": item.get("fecha"),
        "efectivo": item.get("efectivo"),
        "davivienda": item.get("davivienda"),
        "bancolombia": item.get("bancolombia"),
        "cartera": item.get("cartera"),
        "inventario_hoy": item.get("inventario_hoy"),
        "inventario_ayer": item.get("inventario_ayer"),
        "ruta": item.get("ruta"),
        "aux_ops": item.get("aux_ops"),
        "cogs": item.get("cogs"),
        "cash_margin": item.get("cash_margin"),
        "efectivo_total": item.get("efectivo_total"),
        "davivienda_total": item.get("davivienda_total"),
        "bancolombia_total": item.get("bancolombia_total"),
        "cartera_total": item.get("cartera_total"),
        "cierre_total": item.get("cierre_total"),
        "deuda_total" : item.get("deuda_total")
        } for item in cierres])

# Endpoint para obtener un cierre por ID
@cierres_api.route('/<id>/', methods=['GET'])
def get_cierre(id):
    try:
        cierre = Cierre.obtener_por_id(id)
        if cierre:
            return jsonify(json_util.dumps(cierre)), 200
        else:
            return jsonify({"error": "Cierre no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para crear un nuevo cierre
@cierres_api.route('/<fecha_in>', methods=['POST'])
def create_cierre(fecha_in):
    ruta = Route.find_by_date(fecha_in)
    inventario_hoy = Inventory.total_by_date(fecha_in)
    fecha_ayer = (datetime.strptime(fecha_in, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    inventario_ayer = Inventory.total_by_date(fecha_ayer)
    cogs = Purchase.total_by_date(fecha_in)
    aux_ops = Cost.total_by_date_type(fecha_in)
    efectivo_total = 0
    davivienda_total = 0
    bancolombia_total = 0
    cartera_total = 0
    cierre_total = 0
    efectivo = 0
    davivienda = 0
    bancolombia = 0
    cartera = 0
    deuda_total = 0
    orders_with_cartera = Order.find_by_status("Pendiente de pago")
    for order in orders_with_cartera:
        cartera_total += int(order.get("total"))
    cost_ruta = ruta.get("cost")
    stops = ruta.get("stops")
    for stop in stops:
        if stop.get("payment_method") == "Davivienda" and stop.get("status") == "Pagada":
            davivienda = davivienda + (int(stop.get("total_charged")) or 0)
        if stop.get("payment_method") == "Bancolombia" and stop.get("status") == "Pagada":
            bancolombia = bancolombia + (int(stop.get("total_charged")) or 0)
        if stop.get("payment_method") == "Efectivo"  and stop.get("status") == "Pagada":
            efectivo = efectivo + (int(stop.get("total_charged")) or 0)
        if stop.get("status") != "Pagada":
            cartera = cartera + (int(stop.get("total_charged")) or 0)
    cash_margin = (davivienda + bancolombia + efectivo + cartera + inventario_hoy) - (cost_ruta + aux_ops + cogs + inventario_ayer)
    try:
        data = request.get_json()
        nuevo_cierre = Cierre(
            fecha=fecha_in,
            efectivo=efectivo,
            davivienda=davivienda,
            bancolombia=bancolombia,
            cartera=cartera,
            inventario_hoy=inventario_hoy,
            inventario_ayer=inventario_ayer,
            ruta=cost_ruta,
            aux_ops=aux_ops,
            cogs=cogs,
            cash_margin=cash_margin,
            efectivo_total = efectivo_total,
            davivienda_total = davivienda_total,
            bancolombia_total = bancolombia_total,
            cartera_total = cartera_total,
            cierre_total = cierre_total,
            deuda_total = deuda_total
        )
        id_cierre = nuevo_cierre.crear()
        return jsonify({"message": "Cierre creado", "id": str(id_cierre)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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