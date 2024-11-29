from flask import Blueprint, jsonify, request
from models.product import Product
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import json
from pymongo import MongoClient
from openpyxl import Workbook
product_api = Blueprint('product', __name__)

# Ruta para crear un nuevo product
@product_api.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    print(data)
    name = data.get('name')
    unit = data.get('unit')
    category = data.get('category')
    sku = data.get('sku')  
    price_sale = float(data.get('price_sale')) if data.get('price_sale') else 0
    price_purchase = float(data.get('price_purchase')) if data.get('price_purchase') else 0
    discount = float(data.get('discount')) if data.get('discount') else 0
    margen = float(data.get('margen')) if data.get('margen') else 0
    iva = data.get('iva').lower()  if bool(data.get('iva')) else False
    iva_value = float(data.get('iva_value')) if data.get('iva_value') else 0
    description = data.get('description')
    image = data.get('image')
    status = data.get('status')
    quantity = data.get('quantity')
    step_unit = data.get('step_unit')
    root = data.get('root')
    child = data.get('child')
    step_unit_sipsa = data.get('step_unit_sipsa')
    factor_volumen = data.get('factor_volumen')
    sipsa_id = data.get('sipsa_id')
    last_price_purchase = data.get('price_purchase') 
    proveedor = ''
    rate_root = 0
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
        quantity = quantity,
        step_unit_sipsa = step_unit_sipsa,
        step_unit = step_unit,
        factor_volumen = factor_volumen,
        sipsa_id = sipsa_id,
        last_price_purchase = last_price_purchase,
        proveedor= proveedor,
        rate_root = rate_root,
        root = root,
        child = child

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
    root   =   data.get('root')
    child   =  data.get('child')
    step_unit  = data.get('step_unit')
    last_price_purchase = data.get('last_price_purchase')
    proveedor = data.get('proveedor')
    rate_root = data.get('rate_root')
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
    product.last_price_purchase = last_price_purchase or product.last_price_purchase
    product.root = root or product.root
    product.child = child or product.child
    product.step_unit = step_unit or product.step_unit
    product.proveedor = proveedor or product.proveedor
    product.rate_root = rate_root or product.rate_root
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
            "quantity" : product["quantity"],
            "step_unit" :  product["step_unit"],
            "step_unit_sipsa" :  product["step_unit_sipsa"],
            "factor_volumen" : product["factor_volumen"],
            "sipsa_id" : product["sipsa_id"],
            "root" : product["root"],
            "child" : product["child"],
            "last_price_purchase" : product["last_price_purchase"]
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
            "quantity" : product["quantity"],
            "root" : product["root"],
            "child" : product["child"],
            "proveedor" : product["proveedor"],
            "step_unit" : product["step_unit"],
            "rate_root" : product["rate_root"],
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

@product_api.route('/products/syncsheet', methods=['POST'])
def syncsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    def authenticate():
        try:
            if os.name == 'posix':  # Linux o macOS
                path_file = '/home/ubuntu/frescapp/admin/backend/utils/'
            elif os.name == 'nt':  # Windows
                path_file = 'C:/Users/USUARIO/Documents/frescapp/admin/backend/utils/'
            else:
                raise EnvironmentError("Unsupported OS")
                
            credential_path = os.path.join(path_file, 'credentials_spread.json')
            if not os.path.exists(credential_path):
                raise FileNotFoundError(f"El archivo de credenciales no se encontró en {credential_path}")
            
            creds = Credentials.from_service_account_file(credential_path, scopes=scope)
            return creds
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    try:
        credentials = authenticate()
        if isinstance(credentials, tuple):
            return credentials  # If authenticate returned an error response
        client = gspread.authorize(credentials)
    except Exception as e:
        return jsonify({'error': f"Error al autorizar con Google Sheets: {str(e)}"}), 500
    try:
        spreadsheet_id = "1efvIDyxsO0n2A4P_lZj1BUNy-SV_5d5zm9m8CMUI9mc"
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.get_worksheet(1)
        records = worksheet.get_all_records()
    except Exception as e:
        return jsonify({'error': f"Error al acceder a Google Sheets: {str(e)}"}), 500
    try:
        df = pd.DataFrame(records)
        df = df[df['status'] == 'active']
        df = df.drop(columns=['pricing'], errors='ignore')
        df['iva'] = df['iva'].astype(bool)
        df['quantity'] = 0
        json_data = df.to_json(orient='records', date_format='iso')
    except Exception as e:
        return jsonify({'error': f"Error al procesar datos de Google Sheets: {str(e)}"}), 500
    
    try:
        mongo_client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
        db = mongo_client['frescapp']
        collection = db['products']
        collection.delete_many({})
        data = json.loads(json_data)
        collection.insert_many(data)
        collection.update_many(
            {},
            [
                { '$set': { 'price_sale': { '$toDouble': "$price_sale" } } },
                { '$set': { 'discount': { '$toDouble': "$discount" } } },
                { '$set': { 'margen': { '$toDouble': "$margen" } } },
                { '$set': { 'iva_value': { '$toDouble': "$iva_value" } } },
                { '$set': { 'price_purchase': { '$toDouble': "$price_purchase" } } },
                { '$set': { 'description': { '$toString': "$description" } } },
                { '$set': { 'root': { '$toString': "$root" } } },
                { '$set': { 'rate': { '$toDouble': "$rate" } } },
                { '$set': { 'quantity': { '$toDouble': "$quantity" } } },
                { '$set': { 'step_unit': { '$toDouble': "$step_unit" } } },
                { '$set': { 'rate_root': { '$toDouble': "$rate_root" } } }
            ]
        )
    except Exception as e:
        return jsonify({'error': f"Error al interactuar con MongoDB: {str(e)}"}), 500
    return jsonify({"message": "Productos actualizados."}),  200


