from flask import Blueprint, jsonify, request
from models.route import Route
from pymongo import MongoClient
from datetime import datetime

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
            "payment_method": "",
            "checkin_time": "",
            "checkin_latitude": "",
            "checkin_longitude": "",
            "order": index,
            "status": "Por entregar"
        }
        stops.append(stop)

    route = Route(route_number=route_number, close_date=close_date, driver=driver, stops=stops, cost=cost)
    route_id = route.save()

    return jsonify({'message': 'Route created successfully', 'route_id': route_id}), 201

@route_api.route('/route', methods=['PUT'])
def update_route():
    data = request.get_json()
    route_id = data.get('_id')

    # Obtener datos actualizados
    route_number = data.get('route_number')
    close_date = data.get('close_date')
    driver = data.get('driver')
    cost = data.get('cost', 0)
    stops = data.get('stops', [])

    # Buscar la ruta como diccionario y crear instancia de Route
    route_data = Route.object(route_id)
    if not route_data:
        return jsonify({'message': 'Route not found'}), 404

    # Crear la instancia de Route
    route = Route(
        id=route_id,
        route_number=route_number or route_data.get('route_number'),
        close_date=close_date or route_data.get('close_date'),
        driver=driver or route_data.get('driver'),
        cost=cost if cost is not None else route_data.get('cost'),
        stops=stops or route_data.get('stops')
    )

    # Guardar los cambios con el método update de la instancia
    route.update()
    
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
    route = Route.object(route_id) 
    if route:
        route.delete_route()
        return jsonify({'message': 'Route deleted successfully'}), 200
    return jsonify({'message': 'Route not found'}), 404
