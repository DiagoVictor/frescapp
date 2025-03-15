from flask import Blueprint, jsonify, request
from models.route import Route
from pymongo import MongoClient
from datetime import datetime
from werkzeug.utils import secure_filename
import os,json
from werkzeug.utils import secure_filename
from flask import send_from_directory
from models.order import Order

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
routes_collection = db['routes']
orders_collection = db['orders']
counters_collection = db['counters']
route_api = Blueprint('route', __name__)

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
    cost = data.get('cost', 0)

    if not driver or not close_date:
        return jsonify({'message': 'Missing required fields'}), 400

    route_number = get_next_route_number()
    orders = list(orders_collection.find({"delivery_date": close_date}))

    if not orders:
        return jsonify({"message": "No orders found for the given delivery date."}), 404

    stops = []
    for index, order in enumerate(orders, start=1):
        stop = {
            "total_to_charge": sum(item['price_sale'] * item['quantity'] for item in order['products']),
            "quantity_sku": len(order['products']),
            "address": order.get('deliveryAddress'),
            "phone": order.get('customer_phone'),
            "client_name": order.get('customer_name'),
            "total_charged": sum(item['price_sale'] * item['quantity'] for item in order['products']), 
            "payment_method": order["paymentMethod"],
            "slot" : order["deliverySlot"],
            "open_hour" : order["open_hour"],
            "order": index,
            "order_number" : order.get('order_number'),
            "status": "Por entregar"
        }
        stops.append(stop)

    route = Route(route_number=route_number, close_date=close_date, driver=driver, stops=stops, cost=cost)
    route_id = route.save()

    return jsonify({'message': 'Route created successfully', 'route_id': route_id}), 201

UPLOAD_FOLDER = '/home/ubuntu/evidences'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}  # Tipos de archivo permitidos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@route_api.route('/route', methods=['PUT'])
def update_route():
    # Leer datos del formulario
    data = request.form.get('route')  # El campo `route` enviado como string JSON
    evidence = request.files.get('evidence')  # Archivo adjunto

    if not data:
        return jsonify({'message': 'Missing route data'}), 400

    try:
        # Convertir el string JSON a un diccionario
        route_data = json.loads(data)
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON format'}), 400

    route_id = route_data.get('id')

    if not route_id:
        return jsonify({'message': 'Missing route ID'}), 400

    # Buscar la ruta en la base de datos
    existing_route = Route.object(route_id)  # Esto retorna un diccionario
    if not existing_route:
        return jsonify({'message': 'Route not found'}), 404

    # Crear una instancia de la clase Route usando los datos obtenidos
    route_instance = Route(
        id=existing_route['id'],
        route_number=existing_route.get('route_number'),
        close_date=existing_route.get('close_date'),
        driver=existing_route.get('driver'),
        cost=existing_route.get('cost'),
        stops=existing_route.get('stops')
    )

    # Actualizar los datos de la ruta
    route_instance.route_number = route_data.get('route_number', route_instance.route_number)
    route_instance.close_date = route_data.get('close_date', route_instance.close_date)
    route_instance.driver = route_data.get('driver', route_instance.driver)
    route_instance.cost = route_data.get('cost', route_instance.cost)
    route_instance.stops = route_data.get('stops', route_instance.stops)

    # Guardar el archivo de evidencia si está presente
    if evidence and allowed_file(evidence.filename):
        filename = secure_filename(evidence.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        evidence.save(filepath)

    # Guardar los cambios en la base de datos
    route_instance.update()
    stops = route_data.get('stops', [])
    for stop in stops:
        order_number = stop.get('order_number')
        status = stop.get('status')

        if order_number and status:
            orders_collection.update_one({"order_number" : order_number},{"$set": { "status": status}})
        else:
            print("Missing order_number or status for stop")
    return jsonify({'message': 'Route updated successfully'}), 200


@route_api.route('/routes', methods=['GET'])
def list_routes():
    routes_cursor = Route.objects()
    route_data = [
        {
            "id": str(route["_id"]),
            "route_number": route["route_number"],
            "close_date": route["close_date"],
            "driver": route["driver"],
            "stops": route["stops"],
            "status": "creada",
            "cost": route["cost"]
        }
        for route in routes_cursor
    ]   
    return jsonify(route_data), 200

@route_api.route('/route/<string:route_number>', methods=['GET'])
def get_route(route_number):
    route = Route.find_by_route_number(route_number)
    
    if not route:
        return jsonify({'message': 'Route not found'}), 404
    
    # Convertimos `_id` a `str` si está presente
    if '_id' in route:
        route['_id'] = str(route['_id'])
        
    return jsonify(route), 200


@route_api.route('/route/<string:route_id>', methods=['DELETE'])
def delete_route(route_id):
    # Buscar la ruta como diccionario
    route_data = Route.object(route_id)
    if not route_data:
        return jsonify({'message': 'Route not found'}), 404

    # Convertir el diccionario a una instancia de la clase Route
    route_instance = Route(
        id=route_data['id'],
        route_number=route_data.get('route_number'),
        close_date=route_data.get('close_date'),
        driver=route_data.get('driver'),
        cost=route_data.get('cost'),
        stops=route_data.get('stops')
    )

    # Llamar al método para eliminar la ruta
    route_instance.delete_route()
    return jsonify({'message': 'Route deleted successfully'}), 200

@route_api.route('/route/evidence/<string:filename>', methods=['GET'])
def get_evidence(filename):
    """
    Endpoint para obtener un archivo de evidencia por su nombre.
    """
    if not allowed_file(filename):
        return jsonify({'message': 'Invalid file type'}), 400

    # Verificar si el archivo existe en el directorio de evidencias
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'message': 'Evidence file not found'}), 404

    # Enviar el archivo como respuesta
    return send_from_directory(UPLOAD_FOLDER, filename)

@route_api.route('/stop_order_number/<string:order_number>', methods=['GET'])
def get_stop_order(order_number):
    order = Order.find_by_order_number(order_number)
    route = Route.find_by_date(order.delivery_date)
    stops = route.get("stops")
    for stop in stops:
        if stop.get("order_number") == str(order_number):
            return jsonify(stop), 200        
    return None, 400
