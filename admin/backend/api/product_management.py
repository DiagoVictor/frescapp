from flask import Blueprint, jsonify, request
from models.product import Product
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal

product_api = Blueprint('product', __name__)

# Ruta para crear un nuevo product
@product_api.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')  
    price_sale = Decimal(data.get('price_sale')) if data.get('price_sale') else None
    price_purchase = Decimal(data.get('price_purchase')) if data.get('price_purchase') else None
    discount = Decimal(data.get('discount')) if data.get('discount') else None
    margen = Decimal(data.get('margen')) if data.get('margen') else None
    iva = data.get('iva').lower()  if data.get('iva') else None
    iva_value = Decimal(data.get('iva_value')) if data.get('iva_value') else None
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
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
        status = status,
        quantity = quantity
    )
    product.save()
    return jsonify({'message': 'Product created successfully'}), 201

# Ruta para actualizar un usuario existente
@product_api.route('/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else None
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else None
    discount = float(data.get('discount')) if data.get('discount') else None
    margen = float(data.get('margen')) if data.get('margen') else None
    iva = data.get('iva').lower()  if data.get('iva') else None
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else None
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')

    product = Product.object(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.id = product_id
    product.name = name or product.name
    product.unit = unit or product.unit
    product.category = category or product.category
    product.sku = sku or product.sku
    product.price_sale = price_sale if price_sale is not None else product.price_sale
    product.price_purchase = price_purchase if price_purchase is not None else product.price_purchase
    product.discount = discount if discount is not None else product.discount
    product.margen = margen if margen is not None else product.margen
    product.iva = iva or product.iva
    product.iva_value = iva_value if iva_value is not None else product.iva_value
    product.description = description or product.description
    product.image = image or product.image
    product.status = status or product.status
    product.quantity = quantity or product.quantity
    product.updated()

    return jsonify({'message': 'Product updated successfully'}), 200


@product_api.route('/products', methods=['GET'])
def list_product():
    # Filtrar solo los productos con status "active"
    products_cursor = Product.objects(status="active")

    # Construir los datos del producto para la respuesta JSON
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
            "status": product["status"],
            "quantity" : product["quantity"]
        }
        for product in products_cursor
    ]

    # Convertir los datos del producto a formato JSON
    products_json = json.dumps(product_data)

    # Devolver la respuesta JSON con el código de estado 200 (OK)
    return products_json, 200

@product_api.route('/products_customer/<string:customer_email>', methods=['GET'])
def list_product_customer(customer_email):
    # Filtrar solo los productos con status "active"
    products_cursor = Product.objects_customer(status="active",customer_email=customer_email)

    # Construir los datos del producto para la respuesta JSON
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
            "status": product["status"],
            "quantity" : product["quantity"]
        }
        for product in products_cursor
    ]

    # Convertir los datos del producto a formato JSON
    products_json = json.dumps(product_data)

    # Devolver la respuesta JSON con el código de estado 200 (OK)
    return products_json, 200

@product_api.route('/products/update_prices', methods=['PUT'])
def update_product_prices():
    data = request.get_json()
    sku_price_list = data.get('sku_price_list')

    if not sku_price_list:
        return jsonify({'message': 'No SKU price list provided'}), 400

    for sku_price in sku_price_list:
        sku = sku_price.get('sku')
        price_sale = float(sku_price.get('price_sale'))
        if not sku:
            return jsonify({'message': 'SKU is missing in SKU price list'}), 400
        product = Product.find_by_sku(sku=sku)

        if not product:
            return jsonify({'message': f'Product with SKU {sku} not found'}), 404
        product.price_sale = float(price_sale)
        product.id = sku_price.get('id')
        product.updated()
    return jsonify({'message': 'Prices updated successfully'}), 200