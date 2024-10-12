from flask import Blueprint, jsonify, request
from models.route import Route  # Asumiendo que la clase Route está en models.route
from pymongo import MongoClient
import json
from datetime import datetime

# Inicializar la conexión a MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
routes_collection = db['routes']
orders_collection = db['orders']
counters_collection = db['counters']
route_api = Blueprint('route', __name__)

# Función para incrementar el contador en la colección 'counter'
def get_next_route_number():
    counter = counters_collection.find_one_and_update(
        {'_id': 'route_number'},
        {'$inc': {'sequence_value': 1}},
        return_document=True,
        upsert=True
    )
    return counter['sequence_value']

@route_api.route('/route', methods=['POST'])
def create_route():
    data = request.get_json()
    close_date = data.get('close_date')
    driver = data.get('driver')

    # Validar campos obligatorios
    if not driver or not close_date:
        return jsonify({'message': 'Missing required fields'}), 400

    # Generar route_number automáticamente a partir del contador
    route_number = counters_collection.find_one_and_update(
        {"_id": "route_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )["sequence_value"]

    # Extraer las órdenes para la fecha de entrega proporcionada
    orders = list(orders_collection.find({"delivery_date": close_date}))

    if not orders:
        return jsonify({"message": "No orders found for the given delivery date."}), 404

    # Crear las paradas (stops) con los detalles de cada orden
    stops = []
    for order in orders:
        stop = {
            "total_to_charge": sum(item['price_sale'] * item['quantity'] for item in order['products']),  # Total a cobrar
            "quantity_sku": len(order['products']),  # Conteo total de SKUs a entregar
            "address": order.get('deliveryAddress'),  # Dirección del cliente
            "phone": order.get('customer_phone'),  # Teléfono del cliente
            "client_name": order.get('customer_name')  # Nombre del cliente
        }
        stops.append(stop)

    # Crear el documento de la ruta
    route = {
        "route_number": route_number,
        "close_date": close_date,
        "driver": driver,
        "stops": stops  # Agregar las paradas a la ruta
    }

    # Guardar la ruta en la base de datos
    routes_collection.insert_one(route)

    return jsonify({'message': 'Route created successfully', 'route_number': route_number}), 201

# Ruta para actualizar una ruta existente
@route_api.route('/routes/<string:route_id>', methods=['PUT'])
def update_route(route_id):
    data = request.get_json()
    route_number = data.get('route_number')
    close_date_str = data.get('close_date')
    driver = data.get('driver')

    route = Route.object(route_id)
    if not route:
        return jsonify({'message': 'Route not found'}), 404

    # Actualizar solo los campos que se proporcionen
    route.route_number = route_number or route.route_number
    if close_date_str:
        try:
            route.close_date = datetime.strptime(close_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({'message': 'Invalid date format, use YYYY-MM-DD HH:MM:SS'}), 400
    route.driver = driver or route.driver

    route.update()

    return jsonify({'message': 'Route updated successfully'}), 200

# Ruta para listar todas las rutas
@route_api.route('/routes', methods=['GET'])
def list_routes():
    routes_cursor = Route.objects()  # Obtener todas las rutas

    # Construir los datos de la ruta para la respuesta JSON
    route_data = [
        {
            "id": str(route["_id"]),
            "route_number": route["route_number"],
            "close_date": route["close_date"],
            "driver": route["driver"],
            "stops": route["stops"]
        }
        for route in routes_cursor
    ]

    # Convertir los datos de la ruta a formato JSON
    routes_json = json.dumps(route_data)

    # Devolver la respuesta JSON con el código de estado 200 (OK)
    return routes_json, 200
