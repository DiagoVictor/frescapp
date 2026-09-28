from flask import Blueprint, jsonify, request
from models.customer import Customer
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import requests
import time
from pymongo import MongoClient
from models.order import Order
from models.invoice_resolution import InvoiceResolution

alegra_api = Blueprint('alegra', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']
purchases = db['purchases']
invoice_counter = db['invoice_counter'] 

# URL base y cabeceras para la API de Alegra
url_clients = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"
url_doc_soportes = "https://api.alegra.com/api/v1/bills"
url_suppliers = "https://api.alegra.com/api/v1/contacts"
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"  # Reemplaza esto con tus credenciales
}
def get_all_clients():
    clients = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_clients}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            clients.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de clientes: {response.status_code} - {response.text}")
            break
    return clients

# Función para obtener todos los productos con paginación
def get_all_items():
    items = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            items.extend(data)
            start += limit
        else:
            print(f"Error al obtener la lista de productos: {response.status_code} - {response.text}")
            break
    return items

# Función para buscar el cliente en la lista por identificación
def find_client_by_identification(clients, identification):
    for client in clients:
        if client.get("identificationObject", {}).get("number") == identification:
            return client
    return None

# Función para buscar el producto en la lista por referencia
def find_item_by_reference(items, reference):
    for item in items:
        if item.get("reference") == reference:
            return item
    return None

# Función para transformar y enviar la factura
def transform_and_send_invoice(order, client, items, resolution):
    client_data = {
        "id": client["id"],  
        "name": client["name"],
        "identification": client["identificationObject"]["number"],
        "phonePrimary": client["phonePrimary"],
        "email": client["email"],
        "address": {
            "address": client["address"]["address"],
            "department": client["address"]["department"],
            "city": client["address"]["city"]
        },
        "kindOfPerson": client["kindOfPerson"],
        "regime": client["regime"],
        "identificationObject": client["identificationObject"]
    }

    items_data = []
    for product in sorted(list(order['products']), key=lambda x: x['name']):
        item = find_item_by_reference(items, product["sku"])
        if item:
            items_data.append({
                "id": item["id"],
                "name": product["name"],
                "description": "",
                "price": product["price_sale"],
                "discount": 0,
                "reference": product["sku"],
                "quantity": product["quantity"],
                "unit": "unit",
                "tax": [],
                "total": product["price_sale"] * product["quantity"]
            })

    invoice_data = {
        "id": order["order_number"],  # Este campo debe ser único para cada factura
        "date": order["delivery_date"],
        "dueDate": order["delivery_date"],
        "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "observations": None,
        "anotation": "",
        "termsConditions": "Esta factura se asimila en todos sus efectos a una letra de cambio de conformidad con el Art. 774 del código de comercio. Autorizo que en caso de incumplimiento de esta obligación sea reportado a las centrales de riesgo, se cobraran intereses por mora.",
        "status": "open",
        "client": client_data,
        "purchaseOrderNumber":  str(order["order_number"]),
        # Alegra asigna el consecutivo de la resolución activa (ver admin > Resoluciones)
        "numberTemplate": {
            "id": resolution["alegra_template_id"],
            "prefix": resolution["prefix"],
            "text": resolution["text"],
            "documentType": "invoice",
            "isElectronic": True
        },
        "subtotal": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "discount": order["discount"],
        "tax": 0,
        "total": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "totalPaid": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "balance": 0,
        "decimalPrecision": "0",
        "warehouse": {
            "id": "1",
            "name": "Principal"
        },
        "term": "De contado",
        "type": "NATIONAL",
        "operationType": "STANDARD",
        "paymentForm": "CASH",
        "paymentMethod": "CASH",
        "payments": [
        {
            "amount": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
            "paymentMethod": "cash",
            "date": order["delivery_date"],
            "account": { "id": 1 },
        }
        ],
        "seller": None,
        "priceList": {
            "id": 1,
            "name": "General"
        },
        "items": items_data,
        "costCenter": None,
        "printingTemplate": {
            "id": "7",
            "name": "Clásico (Carta electrónica)",
            "pageSize": "letter"
        }
    }
    # URL y cabeceras para la API de Alegra
    url_invoice = "https://api.alegra.com/api/v1/invoices/"
    response = requests.post(url_invoice, headers=headers, json=invoice_data)
    return response

def get_all_suppliers():
    suppliers = []
    start, limit = 0, 30
    while True:
        response = requests.get(f"{url_suppliers}?type=provider&start={start}&limit={limit}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            suppliers.extend(data)
            start += limit
        else:
            print(f"Error al obtener proveedores: {response.status_code} - {response.text}")
            break
    return suppliers

def find_supplier_by_nit(suppliers, nit):
    return next((supplier for supplier in suppliers if str(supplier.get("identification")) == nit), None)

def find_item_by_reference(items, reference):
    return next((item for item in items if item.get("reference") == reference), None)

def get_and_increment_invoice_number():
    invoice_data = invoice_counter.find_one_and_update({}, {"$inc": {"last_invoice": 1}}, upsert=True, return_document=True)
    return invoice_data['last_invoice']

def send_order_invoice(order_number, clients=None, items=None):
    """Crea la factura de un pedido en Alegra con la resolución activa. Devuelve (mensaje, status_code)."""
    order = collection.find_one({"order_number": order_number})
    if not order:
        return f"No se encontró la orden con número {order_number}", 400
    if order.get("alegra_id") not in (None, "", "000"):
        return f"La orden {order_number} ya tiene factura en Alegra ({order.get('invoice_number', order['alegra_id'])})", 409
    resolution = InvoiceResolution.get_active()
    error = InvoiceResolution.check_usable(resolution)
    if error:
        return error, 400
    clients = clients if clients is not None else get_all_clients()
    items = items if items is not None else get_all_items()
    client = find_client_by_identification(clients, order["customer_documentNumber"].split("-")[0])
    if not client:
        return f"No se encontró un cliente con identificación {order['customer_documentNumber']}", 400
    res = transform_and_send_invoice(order, client, items, resolution)
    if str(res.status_code) != '201':
        return res.text, res.status_code
    invoice = res.json()
    number_template = invoice.get("numberTemplate") or {}
    update = {"alegra_id": invoice.get("id"), "invoice_resolution_id": resolution["id"]}
    if number_template.get("fullNumber"):
        update["invoice_number"] = number_template["fullNumber"]
    collection.update_one({"order_number": order_number}, {"$set": update})
    if str(number_template.get("number", "")).isdigit():
        InvoiceResolution.register_used_number(resolution["id"], number_template["number"])
    return res.text, res.status_code

def func_send_invoice(order_number):
    message, status_code = send_order_invoice(order_number)
    return jsonify({"message": message}), status_code

def pending_invoice_orders(days):
    """Pedidos entregados en los últimos `days` días que no tienen factura en Alegra."""
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    orders = collection.find({
        "delivery_date": {"$gte": start, "$lte": end},
        "$or": [{"alegra_id": "000"}, {"alegra_id": {"$exists": False}}, {"alegra_id": None}]
    }).sort("delivery_date", 1)
    return start, end, [{
        "order_number": o["order_number"],
        "delivery_date": o.get("delivery_date"),
        "customer_name": o.get("customer_name"),
        "customer_documentNumber": o.get("customer_documentNumber"),
        "total": o.get("total"),
    } for o in orders]

def func_send_purchase(fecha):
    order = purchases.find_one({"date": fecha})
    suppliers = get_all_suppliers()
    items = get_all_items()
    
    grouped_purchases = {}

    for producto in order['products']:
        proveedor_local = producto.get('proveedor')
        if isinstance(proveedor_local, dict) and proveedor_local.get('nit'):
            proveedor_alegra = find_supplier_by_nit(suppliers, proveedor_local.get('nit'))
            item_alegra = find_item_by_reference(items, producto['sku'])
            
            if proveedor_alegra and item_alegra and producto['final_price_purchase'] > 0 and producto['status'] == 'Registrado' and producto['proveedor']['typeSupport'] == 'Documento soporte':
                subtotal = producto['final_price_purchase'] * producto['total_quantity']

                # Crear el item del producto
                item_info = {
                    "id": item_alegra['id'],
                    "name": item_alegra['name'],
                    "price": producto['final_price_purchase'],
                    "quantity": producto['total_quantity'],
                    "subtotal": subtotal,
                    "total": subtotal
                }

                # Agrupar productos por proveedor
                if proveedor_alegra['id'] in grouped_purchases:
                    grouped_purchases[proveedor_alegra['id']]['items'].append(item_info)
                else:
                    grouped_purchases[proveedor_alegra['id']] = {
                        "proveedor_id": proveedor_alegra['id'],
                        "proveedor_name": proveedor_alegra['name'],
                        "proveedor_nit": proveedor_alegra['identification'],
                        "items": [item_info]
                    }

    # Convertir el diccionario a una lista
    grouped_purchases_list = [value for value in grouped_purchases.values()]

    facturas_creadas = []
    errores = []

    # Realizar las llamadas a la API y actualizar estado en MongoDB
    for purchase in grouped_purchases_list:
        # Obtener el número de factura incremental
        invoice_number = get_and_increment_invoice_number()

        # Calcular el total de la factura sumando los subtotales de los ítems
        total = sum(item['subtotal'] for item in purchase['items'])
        payload = {
            "numberTemplate": {
                "number": str(invoice_number),  
                "id": "17"  
            },
            "purchases": {"items": purchase['items']},
            "stamp": {"generateStamp": True},
            "billOperationType": "INDIVIDUAL",
            "date": fecha,
            "dueDate": fecha,
            "provider": int(purchase['proveedor_id']),
            "paymentMethod": "CASH",
            "paymentType": "CASH",
            "termsConditions": "Autorización de numeración de facturación",
            "payments": [
                {
                    "account": { "id": 1 },
                    "date": fecha,
                    "amount": total,
                    "paymentMethod": "cash"
                }
            ]
        }

        response = requests.post(url_doc_soportes, headers=headers, json=payload)
            # Actualizar en MongoDB
        purchases.update_many(
            {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
            {
                "$set": {
                    "products.$[elem].invoice": invoice_number, 
                    "products.$[elem].status": "Facturada"
                }
            },
            array_filters=[{"elem.proveedor.nit": purchase['proveedor_nit']}]
        )

        purchases.update_many(
            {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
            {
                "$set": {"status": "Facturada"}
            }
        )

        facturas_creadas.append({
            "proveedor_name": purchase['proveedor_name'],
            "invoice_number": invoice_number
        })
    else:
        errores.append({
            "proveedor_name": purchase['proveedor_name'],
            "error": response.text
        })
    return jsonify({
        "facturas_creadas": facturas_creadas,
        "errores": errores
    }), 200 

def emit_invoice(alegra_id):
    """Timbra (emite ante la DIAN) una factura ya creada en Alegra."""
    url = 'https://api.alegra.com/api/v1/invoices/stamp'
    payload = {'ids': [alegra_id]}
    return requests.post(url, headers=headers, json=payload)

@alegra_api.route('/send_invoice/<string:order_number>', methods=['GET'])
def send_invoice(order_number):
    return func_send_invoice(order_number)
@alegra_api.route('/get_invoice/<string:order_number>', methods=['GET'])
def get_invoice(order_number):
    orden = Order.find_by_order_number(order_number)
    url = f"https://api.alegra.com/api/v1/invoices/{orden.alegra_id}?fields=pdf"
    headers = {
        "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"
    }
    response = requests.get(url, headers=headers, stream=True)
    return jsonify(response.json().get('pdf'))

@alegra_api.route('/send_purchase/<string:fecha>', methods=['GET'])
def send_purchase(fecha):
    return func_send_purchase(fecha)

# ---------------- Resoluciones de facturación ----------------

@alegra_api.route('/resolutions', methods=['GET'])
def list_resolutions():
    return jsonify(InvoiceResolution.get_all()), 200

@alegra_api.route('/resolutions/active', methods=['GET'])
def active_resolution():
    resolution = InvoiceResolution.get_active()
    return jsonify({"resolution": resolution, "error": InvoiceResolution.check_usable(resolution)}), 200

@alegra_api.route('/resolutions', methods=['POST'])
def create_resolution():
    data = request.get_json() or {}
    missing = [f for f in ("alegra_template_id", "prefix", "from_number", "to_number", "resolution_number", "resolution_date", "valid_until") if not data.get(f)]
    if missing:
        return jsonify({"message": f"Faltan campos: {', '.join(missing)}"}), 400
    return jsonify(InvoiceResolution.create(data)), 201

@alegra_api.route('/resolutions/<string:resolution_id>', methods=['PUT'])
def update_resolution(resolution_id):
    resolution = InvoiceResolution.update(resolution_id, request.get_json() or {})
    if not resolution:
        return jsonify({"message": "Resolución no encontrada"}), 404
    return jsonify(resolution), 200

@alegra_api.route('/resolutions/<string:resolution_id>/activate', methods=['POST'])
def activate_resolution(resolution_id):
    resolution = InvoiceResolution.activate(resolution_id)
    if not resolution:
        return jsonify({"message": "Resolución no encontrada"}), 404
    return jsonify(resolution), 200

@alegra_api.route('/resolutions/<string:resolution_id>', methods=['DELETE'])
def delete_resolution(resolution_id):
    if not InvoiceResolution.delete(resolution_id):
        return jsonify({"message": "No se puede eliminar la resolución activa"}), 400
    return jsonify({"message": "Resolución eliminada"}), 200

@alegra_api.route('/number_templates', methods=['GET'])
def list_number_templates():
    """Numeraciones configuradas en Alegra, para escoger el id de la resolución."""
    response = requests.get("https://api.alegra.com/api/v1/number-templates", headers=headers)
    if response.status_code != 200:
        return jsonify({"message": response.text}), response.status_code
    templates = [t for t in response.json() if t.get("documentType") == "invoice"]
    return jsonify(templates), 200

# ---------------- Facturas pendientes por emitir ----------------

@alegra_api.route('/pending_invoices', methods=['GET'])
def list_pending_invoices():
    days = int(request.args.get('days', 7))
    start, end, orders = pending_invoice_orders(days)
    return jsonify({"start": start, "end": end, "orders": orders}), 200

@alegra_api.route('/pending_invoices', methods=['POST'])
def send_pending_invoices():
    """Crea en Alegra y emite ante la DIAN las facturas pendientes de los últimos `days` días."""
    days = int((request.get_json(silent=True) or {}).get('days', request.args.get('days', 7)))
    resolution = InvoiceResolution.get_active()
    error = InvoiceResolution.check_usable(resolution)
    if error:
        return jsonify({"message": error}), 400

    start, end, orders = pending_invoice_orders(days)
    clients = get_all_clients()
    items = get_all_items()
    enviadas, errores = [], []
    for o in orders:
        message, status_code = send_order_invoice(o["order_number"], clients, items)
        if str(status_code) != '201':
            errores.append({"order_number": o["order_number"], "error": message})
            continue
        order = collection.find_one({"order_number": o["order_number"]})
        time.sleep(3)
        stamp = emit_invoice(order["alegra_id"])
        enviadas.append({
            "order_number": o["order_number"],
            "invoice_number": order.get("invoice_number"),
            "alegra_id": order["alegra_id"],
            "emitida": stamp.status_code in (200, 201),
            "stamp_response": None if stamp.status_code in (200, 201) else stamp.text,
        })
        time.sleep(3)
    return jsonify({"start": start, "end": end, "enviadas": enviadas, "errores": errores}), 200
