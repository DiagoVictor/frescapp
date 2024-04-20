from flask import Blueprint, jsonify, request
from models.customer import Customer
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime

customer_api = Blueprint('customer', __name__)

# Ruta para crear un nuevo usuario
@customer_api.route('/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    phone = data.get('phone')
    name = data.get('name')
    document = data.get('document')
    document_type = data.get('document_type')
    address = data.get('address')
    restaurant_name = data.get('restaurant_name')
    email = data.get('email')  
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    password = data.get('password')
    category = data.get('category')
    bcrypt = Bcrypt()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    if not phone or not email:
        return jsonify({'message': 'Missing required fields'}), 400

    if Customer.find_by_email(email=email):
        return jsonify({'message': 'Customer already exists'}), 400

    customer = Customer(        
        phone = phone,
        name = name,
        document = document,
        document_type = document_type,
        address = address,
        restaurant_name = restaurant_name,
        email = email,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        password = hashed_password,
        category = category
    )
    customer.save()
    return jsonify({'message': 'Customer created successfully'}), 201

# Ruta para actualizar un usuario existente
@customer_api.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    phone = data.get('phone')
    name = data.get('name')
    document = data.get('document')
    document_type = data.get('document_type')
    address = data.get('address')
    restaurant_name = data.get('restaurant_name')
    email = data.get('email')  
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    category = data.get('category')
    customer = Customer.object(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404
    customer.id = customer_id
    customer.phone = phone or customer.phone
    customer.name = name or customer.name
    customer.document = document or customer.document
    customer.document_type = document_type or customer.document_type
    customer.address = address or customer.address
    customer.restaurant_name = restaurant_name or customer.restaurant_name
    customer.email = email or customer.email
    customer.status =status or customer.status
    customer.created_at = created_at or customer.created_at
    customer.updated_at = updated_at or customer.updated_at
    customer.category = category or customer.category
    customer.updated()
    return jsonify({'message': 'customer updated successfully'}), 200

@customer_api.route('/customers', methods=['GET'])
def list_customers():
    customers_cursor = Customer.objects()
    customer_data = [
        {
         "id": str(customer["_id"]), 
         "phone": customer["phone"], 
         "name": customer["name"], 
         "document": customer["document"], 
         "document_type": customer["document_type"], 
         "address": customer["address"], 
         "restaurant_name": customer["restaurant_name"], 
         "email": customer["email"], 
         "status": customer["status"], 
         "created_at": customer["created_at"], 
         "updated_at": customer["updated_at"], 
         "category": customer["category"]
         }
        for customer in customers_cursor
    ]
    customers_json = json.dumps(customer_data)
    return customers_json, 200
@customer_api.route('/customer/<string:customer_id>', methods=['GET'])
def customer(customer_id):
    customer_object = Customer.object(customer_id)
    if customer_object:
        customer_json = {
            "phone": customer_object.phone,
            "name": customer_object.name,
            "document": customer_object.document,
            "document_type": customer_object.document_type,
            "address": customer_object.address,
            "restaurant_name": customer_object.restaurant_name,
            "email": customer_object.email,
            "status": customer_object.status,
            "created_at": str(customer_object.created_at),
            "updated_at": str(customer_object.updated_at),
            "category": customer_object.category
        }
        return jsonify(customer_json), 200
    else:
        return jsonify({'message': 'Customer not found'}), 404