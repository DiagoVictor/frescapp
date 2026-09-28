from flask import Blueprint, jsonify, request
from ..models.customer import Customer
from ..models.order import Order
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import requests
import time
from pymongo import MongoClient
from ..db import get_db  
from ..models.invoice_resolution import InvoiceResolution

alegra_api = Blueprint('alegra', __name__)

# URL base y cabeceras para la API de Alegra
url_clients = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"
url_doc_soportes = "https://api.alegra.com/api/v1/bills"
url_suppliers = "https://api.alegra.com/api/v1/contacts"
headers = {
    "accept": "application/json",
    "authorization": "Basic ZmVzY2FwcEBnbWFpbC5jb206ZTMxNWIyOTQ2YjY4ZDk0NjExYjA="  # ⚠️ pon esto en variable de entorno luego
}

# ===============================================
# ========== FUNCIONES DE ALEGRA API ============
# ===============================================

def get_all_clients():
    clients = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_clients}?start={start}&limit={limit}", headers=headers, timeout=30)
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


def get_all_items():
    items = []
    start = 0
    limit = 30
    while True:
        response = requests.get(f"{url_items}?start={start}&limit={limit}", headers=headers, timeout=30)
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


def find_client_by_identification(clients, identification):
    for client in clients:
        if client.get("identificationObject", {}).get("number") == identification:
            return client
    return None


def create_client(order, identification):
    document_type = order.get("customer_documentType") or "CC"
    kind_of_person = "PERSON_ENTITY" if document_type == "NIT" else "PERSON_NATURAL"

    client_payload = {
        "name": order.get("customer_name") or identification,
        "identification": identification,
        "identificationObject": {
            "type": document_type,
            "number": identification
        },
        "type": ["client"],
        "kindOfPerson": kind_of_person,
        "regime": "SIMPLIFIED_REGIME",
        "phonePrimary": order.get("customer_phone") or "",
        "email": order.get("customer_email") or "",
        "address": {
            "address": order.get("deliveryAddress") or "",
            "city": "Bogotá, D.C.",
            "department": "Bogotá, D.C."
        }
    }

    response = requests.post(url_clients, headers=headers, json=client_payload, timeout=30)
    if response.status_code in (200, 201):
        return response.json(), None
    error_message = f"Error al crear el cliente {identification} en Alegra: {response.status_code} - {response.text}"
    print(error_message)
    return None, error_message


def find_item_by_reference(items, reference):
    for item in items:
        if item.get("reference") == reference:
            return item
    return None


# ===============================================
# ========== FUNCIONES DE FACTURACIÓN ============
# ===============================================

def transform_and_send_invoice(order, client, items, resolution, invoice_number, invoice_date=None):
    # Fecha de la factura: la de entrega salvo que se indique otra (ej. emisión de pendientes con la fecha actual)
    invoice_date = invoice_date or order["delivery_date"]
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

    items_by_ref = {}
    for i in items:
        items_by_ref.setdefault(i.get("reference"), i)

    items_data = []
    for product in sorted(list(order['products']), key=lambda x: x['name']):
        item = items_by_ref.get(product["sku"])
        if item:
            items_data.append({
                "id": item["id"],
                "name": product["name"],
                "description": "",
                "price": product["price_sale"],
                "discount": product["discount"] if "discount" in product else 0 ,
                "reference": product["sku"],
                "quantity": product["quantity"],
                "unit": "unit",
                "tax": [],
                "total": product["price_sale"] * product["quantity"] * (1 - (product["discount"] / 100) if "discount" in product else 1)
            })

    invoice_data = {
        "id": order["order_number"],  # Este campo debe ser único para cada factura
        "date": invoice_date,
        "dueDate": invoice_date,
        "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "observations": order["deliveryAddress"],
        "anotation": order["deliveryAddress"],
        "termsConditions": "Esta factura se asimila en todos sus efectos a una letra de cambio de conformidad con el Art. 774 del código de comercio. Autorizo que en caso de incumplimiento de esta obligación sea reportado a las centrales de riesgo, se cobraran intereses por mora.",
        "status": "open",
        "client": client_data,
        "purchaseOrderNumber":  str(order["order_number"]),
        # Numeración de la resolución activa (admin > Facturación)
        "numberTemplate": {
            "id": resolution["alegra_template_id"],
            "prefix": resolution["prefix"],
            "number": invoice_number,
            "text": resolution["text"],
            "documentType": "invoice",
            "fullNumber": f"{resolution['prefix']}{invoice_number}",
            "formattedNumber": invoice_number,
            "isElectronic": True
        },
        "subtotal": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "discount": 0,
        "tax": 0,
        "total": sum(item["price_sale"] * item["quantity"] * (1 - (item["discount"] / 100) if "discount" in item else 1) for item in order["products"]),
        "totalPaid": sum(item["price_sale"] * item["quantity"] * (1 - (item["discount"] / 100) if "discount" in item else 1) for item in order["products"]),
        "balance": 0,
        "decimalPrecision": "0",
        "warehouse": {
            "id": "019e8675-7063-73bd-8c98-7e69cea7dab8",
            "name": "Principal"
        },
        "term": "De contado",
        "type": "NATIONAL",
        "operationType": "STANDARD",
        "paymentForm": "CASH",
        "paymentMethod": "CASH",
        "payments": [
        {
            "amount": sum(item["price_sale"] * item["quantity"] * (1 - (item["discount"] / 100) if "discount" in item else 1) for item in order["products"]),
            "paymentMethod": "cash",
            "date": invoice_date,
            "account": { "id": 1 },
        }
        ],
        "seller": None,
        "priceList": {
            "id": "019e8675-7060-7290-a5d6-43826285dfaa",
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
    response = requests.post(url_invoice, headers=headers, json=invoice_data, timeout=30)
    return response

def get_all_suppliers():
    suppliers = []
    start, limit = 0, 30
    while True:
        response = requests.get(f"{url_suppliers}?type=provider&start={start}&limit={limit}", headers=headers, timeout=30)
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


def get_and_increment_invoice_number():
    db = get_db()
    invoice_counter = db['invoice_counter']
    invoice_data = invoice_counter.find_one_and_update({}, {"$inc": {"last_invoice": 1}}, upsert=True, return_document=True)
    return invoice_data['last_invoice']


# Resolución DIAN FVF (formulario 18764116141708) habilitada en Alegra en septiembre de 2026.
DEFAULT_RESOLUTION = {
    "prefix": "FVF",
    "from_number": 1,
    "to_number": 5000,
    "resolution_number": "18764116141708",
    "resolution_date": "2026-09-24",
    "valid_until": "2028-09-24",
    "document_type": "invoice",
}


def ensure_default_resolution():
    """Registra y activa la resolución FVF si aún no existe en la base de datos."""
    if InvoiceResolution.exists(DEFAULT_RESOLUTION["prefix"]):
        return
    response = requests.get("https://api.alegra.com/api/v1/number-templates", headers=headers, timeout=30)
    if response.status_code != 200:
        print(f"No se pudo consultar las numeraciones de Alegra: {response.status_code} - {response.text}")
        return
    template = next((t for t in response.json()
                     if str(t.get("prefix", "")).upper() == DEFAULT_RESOLUTION["prefix"]
                     and t.get("documentType", "invoice") == "invoice"), None)
    if not template:
        print(f"No se encontró la numeración {DEFAULT_RESOLUTION['prefix']} en Alegra")
        return
    InvoiceResolution.create({**DEFAULT_RESOLUTION, "alegra_template_id": template["id"], "active": True})


def get_active_resolution():
    ensure_default_resolution()
    return InvoiceResolution.get_active()


def send_order_invoice(order_number, clients=None, items=None, invoice_date=None):
    """Crea la factura de un pedido en Alegra con la resolución activa. Devuelve (mensaje, status_code)."""
    db = get_db()
    collection = db['orders']

    order = collection.find_one({"order_number": order_number})
    if not order:
        return f"No se encontró la orden {order_number}", 404
    if order.get("alegra_id") not in (None, "", "000"):
        return f"La orden {order_number} ya tiene factura en Alegra ({order.get('invoice_number', order['alegra_id'])})", 409

    resolution = get_active_resolution()
    error = InvoiceResolution.check_usable(resolution)
    if error:
        return error, 400

    if clients is None:
        clients = get_all_clients()
    if items is None:
        items = get_all_items()

    identification = order["customer_documentNumber"].split("-")[0]
    client = find_client_by_identification(clients, identification)
    if not client:
        client, error_message = create_client(order, identification)
        if not client:
            return f"No se encontró y no se pudo crear el cliente {order['customer_documentNumber']} en Alegra: {error_message}", 400
        clients.append(client)

    # Si un envío anterior falló, se reutiliza el número ya reservado para no dejar huecos
    reserved = order.get("invoice_reserved_number")
    if reserved and order.get("invoice_resolution_id") == resolution["id"]:
        invoice_number = reserved
    else:
        invoice_number = InvoiceResolution.next_number(resolution["id"])
        if invoice_number is None:
            return f"La resolución {resolution['prefix']} agotó su rango de numeración.", 400
        collection.update_one({"order_number": order_number}, {"$set": {
            "invoice_reserved_number": invoice_number,
            "invoice_resolution_id": resolution["id"],
        }})

    res = transform_and_send_invoice(order, client, items, resolution, invoice_number, invoice_date)
    print(res.text)
    if res.status_code == 201:
        collection.update_one({"order_number": order_number}, {"$set": {
            "alegra_id": res.json().get("id"),
            "invoice_number": f"{resolution['prefix']}{invoice_number}",
        }})
    return res.text, res.status_code


def func_send_invoice(order_number, clients=None, items=None):
    message, status_code = send_order_invoice(order_number, clients, items)
    return jsonify({"message": message}), status_code


def pending_invoice_orders(days):
    """Pedidos entregados en los últimos `days` días que no tienen factura en Alegra."""
    collection = get_db()['orders']
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
    db = get_db()
    purchases = db['purchases']
    order = purchases.find_one({"date": fecha})

    if not order:
        return jsonify({"message": f"No se encontró compra con fecha {fecha}"}), 404

    suppliers = get_all_suppliers()
    items = get_all_items()

    suppliers_by_nit = {}
    for s in suppliers:
        suppliers_by_nit.setdefault(str(s.get("identification")), s)
    items_by_ref = {}
    for i in items:
        items_by_ref.setdefault(i.get("reference"), i)

    grouped_purchases = {}
    for producto in order['products']:
        proveedor_local = producto.get('proveedor')
        if isinstance(proveedor_local, dict) and proveedor_local.get('nit'):
            proveedor_alegra = suppliers_by_nit.get(proveedor_local.get('nit'))
            item_alegra = items_by_ref.get(producto['sku'])

            if proveedor_alegra and item_alegra and producto['final_price_purchase'] > 0 and producto['status'] == 'Registrado' and producto['proveedor']['typeSupport'] == 'Documento soporte':
                subtotal = producto['final_price_purchase'] * producto['total_quantity']
                item_info = {
                    "id": item_alegra['id'],
                    "name": item_alegra['name'],
                    "price": producto['final_price_purchase'],
                    "quantity": producto['total_quantity'],
                    "subtotal": subtotal,
                    "total": subtotal
                }

                grouped_purchases.setdefault(proveedor_alegra['id'], {
                    "proveedor_id": proveedor_alegra['id'],
                    "proveedor_name": proveedor_alegra['name'],
                    "proveedor_nit": proveedor_alegra['identification'],
                    "items": []
                })["items"].append(item_info)

    facturas_creadas = []
    errores = []

    for purchase in grouped_purchases.values():
        invoice_number = get_and_increment_invoice_number()
        total = sum(item['subtotal'] for item in purchase['items'])

        payload = {
            "numberTemplate": {"number": str(invoice_number), "id": "17"},
            "purchases": {"items": purchase['items']},
            "date": fecha,
            "provider": int(purchase['proveedor_id']),
            "paymentMethod": "CASH",
            "payments": [{"account": {"id": 1}, "date": fecha, "amount": total, "paymentMethod": "cash"}]
        }

        response = requests.post(url_doc_soportes, headers=headers, json=payload, timeout=30)
        if response.status_code == 201:
            purchases.update_many(
                {"products.proveedor.nit": purchase['proveedor_nit'], "date": fecha},
                {"$set": {"status": "Facturada"}}
            )
            facturas_creadas.append({"proveedor_name": purchase['proveedor_name'], "invoice_number": invoice_number})
        else:
            errores.append({"proveedor_name": purchase['proveedor_name'], "error": response.text})

    return jsonify({"facturas_creadas": facturas_creadas, "errores": errores}), 200


def emit_invoice(alegra_id):
    url = 'https://api.alegra.com/api/v1/invoices/stamp'
    response = requests.post(url, headers=headers, json={'ids': [alegra_id]}, timeout=30)
    return response


# ===============================================
# ============== RUTAS API ======================
# ===============================================

@alegra_api.route('/send_invoice/<string:order_number>', methods=['GET'])
def send_invoice(order_number):
    return func_send_invoice(order_number)


@alegra_api.route('/get_invoice/<string:order_number>', methods=['GET'])
def get_invoice(order_number):
    orden = Order.find_by_order_number(order_number)
    url = f"https://api.alegra.com/api/v1/invoices/{orden.alegra_id}?fields=pdf"
    response = requests.get(url, headers=headers, stream=True, timeout=30)
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
    resolution = get_active_resolution()
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
    response = requests.get("https://api.alegra.com/api/v1/number-templates", headers=headers, timeout=30)
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
    resolution = get_active_resolution()
    error = InvoiceResolution.check_usable(resolution)
    if error:
        return jsonify({"message": error}), 400

    start, end, orders = pending_invoice_orders(days)
    today = datetime.now().strftime('%Y-%m-%d')
    clients = get_all_clients()
    items = get_all_items()
    enviadas, errores = [], []
    for o in orders:
        message, status_code = send_order_invoice(o["order_number"], clients, items, invoice_date=today)
        if str(status_code) != '201':
            errores.append({"order_number": o["order_number"], "error": message})
            continue
        order = get_db()["orders"].find_one({"order_number": o["order_number"]})
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
