from flask import Blueprint, jsonify, request
from models.product import Product
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime

product_api = Blueprint('product', __name__)

# Ruta para crear un nuevo product
@product_api.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')  
    price_sale = data.get('price_sale')  
    price_purchase = data.get('price_purchase')
    discount = data.get('discount')
    margen = data.get('margen')
    iva = data.get('iva')
    iva_value = data.get('iva_value')
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    if not sku or not name:
        return jsonify({'message': 'Missing required fields'}), 400

    if Product.find_by_sku(sku=sku):
        return jsonify({'message': 'Product already exists'}), 400

    product = Product(        
        name = name,
        unit = unit,
        category = category,
        sku = sku,
        price_sale = price_sale,
        price_purchase = price_purchase,
        discount = discount,
        margen = margen,
        iva = iva,
        iva_value = iva_value,
        description = description,
        image = image,
        status = status
    )
    product.save()
    return jsonify({'message': 'User created successfully'}), 201

# Ruta para actualizar un usuario existente
@product_api.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')  
    price_sale = data.get('price_sale')  
    price_purchase = data.get('price_purchase')
    discount = data.get('discount')
    margen = data.get('margen')
    iva = data.get('iva')
    iva_value = data.get('iva_value')
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    product = Product.object(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    product.id = product_id
    product.name = name or product.name
    product.unit = unit or product.unit
    product.category = category or product.category
    product.sku = sku or product.sku
    product.price_sale =price_sale or product.price_sale
    product.price_purchase = price_purchase or product.price_purchase
    product.discount = discount or product.discount
    product.margen = margen or product.margen
    product.iva = iva or product.iva
    product.iva_value = iva_value or product.iva_value
    product.description = description or product.description
    product.image = image or product.image
    product.status = status or product.status
    product.updated()
    return jsonify({'message': 'product updated successfully'}), 200

@product_api.route('/products', methods=['GET'])
def list_product():
    products_cursor = Product.objects()
    product_data = [
        {
         "id": str(product["_id"]), 
         "name": product["name"], 
         "unit": product["unit"], 
         "category": product["category"], 
         "sku": product["sku"], 
         "price_sale": product["price_sale"], 
         "price_purchase": product["price_purchase"], 
         "discount": product["discount"], 
         "margen": product["margen"], 
         "iva": product["iva"], 
         "iva_value": product["iva_value"], 
         "description": product["description"], 
         "image": product["image"], 
         "status": product["status"]
         }
        for product in products_cursor
    ]
    products_json = json.dumps(product_data)
    return products_json, 200
