from flask import Blueprint, jsonify, request
from models.order import Order
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime

order_api = Blueprint('order', __name__)

@order_api.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('customer_email')
    delivery_date = data.get('delivery_date')
    status = data.get('status')
    created_at = data.get('created_at')  
    updated_at = data.get('updated_at')  
    products = data.get('products')
    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400

    if Order.find_by_order_number(order_number=order_number):
        return jsonify({'message': 'Customer already exists'}), 400

    order = Order(        
        order_number = order_number,
        customer_email = customer_email,
        delivery_date = delivery_date,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        products = products
    )
    order.save()
    return jsonify({'message': 'Order created successfully'}), 201

# Ruta para actualizar un usuario existente
@order_api.route('/customers/<string:customer_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('customer_email')
    delivery_date = data.get('delivery_date')
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    products = data.get('products')
    order = Order.object(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    order.id = order_id
    order.order_number = order_number or order.order_number
    order.customer_email = customer_email or order.customer_email
    order.delivery_date = delivery_date or order.delivery_date
    order.status =status or order.status
    order.created_at = created_at or order.created_at
    order.updated_at = updated_at or order.updated_at
    order.products = products or order.products
    order.updated()
    return jsonify({'message': 'Order updated successfully'}), 200

@order_api.route('/orders', methods=['GET'])
def list_orders():
    orders_cursor = Order.objects()
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"], 
         "customer_email": order["customer_email"], 
         "delivery_date": order["delivery_date"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"], 
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200
