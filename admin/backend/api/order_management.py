from flask import Blueprint, jsonify, request
from models.order import Order
import json
from flask_bcrypt import Bcrypt
from datetime import datetime

order_api = Blueprint('order', __name__)

@order_api.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('email') or  data.get('customer_email')
    customer_phone = data.get('phoneNumber') if data.get('phoneNumber') else data.get('customer_phone')
    customer_documentNumber = data.get('documentNumber') if data.get('documentNumber') else data.get('customer_documentNumber')
    customer_documentType = data.get('documentType') if data.get('documentType') else data.get('customer_documentType')
    customer_name = data.get('customerName') if data.get('customerName') else data.get('customer_name')
    delivery_date = data.get('deliveryDate') if data.get('deliveryDate') else data.get('delivery_date')
    status = data.get('status') or 'Creada'
    created_at = data.get('created_at')  
    updated_at = data.get('updated_at')  
    products = data.get('products')
    total = data.get('total')
    deliverySlot = data.get('deliverySlot')
    paymentMethod = data.get('paymentMethod')
    deliveryAddress = data.get('deliveryAddress') # Nuevo campo: Dirección de entrega
    deliveryAddressDetails = data.get('deliveryAddressDetails') # Nuevo campo: Detalle dirección

    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400

    if Order.find_by_order_number(order_number=order_number):
        return jsonify({'message': 'Order already exists'}), 400

    order = Order(        
        order_number = order_number,
        customer_email = customer_email,
        customer_phone = customer_phone,
        customer_documentNumber = customer_documentNumber,
        customer_documentType = customer_documentType,
        customer_name = customer_name,
        delivery_date = delivery_date,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        products = products,
        total = total,
        deliverySlot = deliverySlot,
        paymentMethod = paymentMethod,
        deliveryAddress = deliveryAddress,
        deliveryAddressDetails = deliveryAddressDetails 
    )
    order.save()
    return jsonify({'message': 'Order created successfully'}), 201

# Ruta para actualizar un usuario existente
@order_api.route('/order/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('email')
    customer_phone = data.get('phoneNumber')
    customer_documentNumber = data.get('documentNumber')
    customer_documentType = data.get('documentType')
    customer_name = data.get('customerName')
    delivery_date = data.get('deliveryDate')
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    products = data.get('products')
    total = data.get('total')
    deliverySlot = data.get('deliverySlot')
    paymentMethod = data.get('paymentMethod')
    deliveryAddress = data.get('deliveryAddress') 
    deliveryAddressDetails = data.get('deliveryAddressDetails') 
    
    order = Order.object(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    order.id = order_id
    order.order_number = order_number or order.order_number
    order.customer_email = customer_email or order.customer_email
    order.customer_phone = customer_phone or order.customer_phone
    order.customer_documentNumber = customer_documentNumber or order.customer_documentNumber
    order.customer_documentType = customer_documentType or order.customer_documentType
    order.customer_name = customer_name or order.customer_name
    order.delivery_date = delivery_date or order.delivery_date
    order.status =status or order.status
    order.created_at = created_at or order.created_at
    order.updated_at = updated_at or order.updated_at
    order.products = products or order.products
    order.total = total or order.total
    order.deliverySlot = deliverySlot or order.deliverySlot
    order.paymentMethod = paymentMethod or order.paymentMethod
    order.deliveryAddress = deliveryAddress or order.deliveryAddress 
    order.deliveryAddressDetails = deliveryAddressDetails or order.deliveryAddressDetails 
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
         "customer_phone": order["customer_phone"], 
         "customer_documentNumber": order["customer_documentNumber"], 
         "customer_documentType": order["customer_documentType"], 
         "customer_name": order["customer_name"], 
         "delivery_date": order["delivery_date"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"], 
         "deliveryAddress": order["deliveryAddress"], # Nuevo campo: Dirección de entrega
         "deliveryAddressDetails": order["deliveryAddressDetails"]  # Nuevo campo: Detalle dirección
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200

@order_api.route('/orders_customer/<string:email>', methods=['GET'])
def list_orders_customer(email):
    orders_cursor = Order.find_by_customer(email)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"], 
         "customer_email": order["customer_email"], 
         "customer_phone": order["customer_phone"], 
         "customer_documentNumber": order["customer_documentNumber"], 
         "customer_documentType": order["customer_documentType"], 
         "customer_name": order["customer_name"], 
         "delivery_date": order["delivery_date"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"], 
         "deliveryAddress": order["deliveryAddress"], # Nuevo campo: Dirección de entrega
         "deliveryAddressDetails": order["deliveryAddressDetails"]  # Nuevo campo: Detalle dirección
         }
        for order in orders_cursor
    ]
    order_data.sort(key=lambda x: x['created_at'], reverse=True)

    orders_json = json.dumps(order_data)
    return orders_json, 200
