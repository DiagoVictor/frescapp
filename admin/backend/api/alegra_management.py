from flask import Blueprint, jsonify, request
from ..models.customer import Customer
from ..models.order import Order
from flask_bcrypt import Bcrypt
from datetime import datetime
import requests
from pymongo import MongoClient
from ..db import get_db  

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

def transform_and_send_invoice(order, client, items):
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

    invoice_number = get_and_increment_sales_invoice_number()

    invoice_data = {
        "id": order["order_number"],  # Este campo debe ser único para cada factura
        "date": order["delivery_date"],
        "dueDate": order["delivery_date"],
        "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "observations": order["deliveryAddress"],
        "anotation": order["deliveryAddress"],
        "termsConditions": "Esta factura se asimila en todos sus efectos a una letra de cambio de conformidad con el Art. 774 del código de comercio. Autorizo que en caso de incumplimiento de esta obligación sea reportado a las centrales de riesgo, se cobraran intereses por mora.",
        "status": "open",
        "client": client_data,
        "purchaseOrderNumber":  str(order["order_number"]),
        "numberTemplate": {
            "id": "1",
            "prefix": "FVE",
            "number": invoice_number,
            "text": "Autorización de numeración de facturación N°18764105685502 de 2026-02-09 Modalidad Factura Electrónica Desde N° FVE1 hasta FVE500 con vigencia hasta 2028-02-09",
            "documentType": "invoice",
            "fullNumber": f"FVE{invoice_number}",
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
            "amount": sum(item["price_sale"] * item["quantity"] * (1 - (item["discount"] / 100) if "discount" in item else 1) for item in order["products"]),
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
        "stamp": {
            "legalStatus": "PENDING",
            "cufe": "216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee",
            "barCodeContent": "NumFac: FRES1281\nFecFac: 2024-07-10\nHorFac: 21:29:49-05:00\nNitFac: 901387528\nDocAdq: 1020808385\nValFac: 165000.00\nValIva: 0.00\nValOtroIm: 0.00\nValTolFac: 165000.00\nCUFE: 216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee\nQRCode: https:\/\/catalogo-vpfe.dian.gov.co\/document\/searchqr?documentkey=216598b481686b59cc4681f36faeb20228f1f53521c1c605b98722abee530405264984a51544241708d8bf4de7ef3bee\n",
            "date": "2024-07-10 21:30:52",
            "warnings": [
                "Regla: FAZ09, Notificación: Debe existir el grupo de información de identificación del bien o servicio",
                "Regla: FAJ43b, Notificación: Nombre informado No corresponde al registrado en el RUT con respecto al Nit suministrado.",
                "Regla: FAJ43b, Notificación: Nombre informado No corresponde al registrado en el RUT con respecto al Nit suministrado.",
                "Regla: RUT01, Notificación: La validación del estado del RUT próximamente estará disponible.",
                "Regla: RUT01, Notificación: La validación del estado del RUT próximamente estará disponible."
            ]
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


def get_and_increment_sales_invoice_number():
    db = get_db()
    invoice_counter = db['sales_invoice_counter']
    invoice_data = invoice_counter.find_one_and_update({}, {"$inc": {"last_invoice": 1}}, upsert=True, return_document=True)
    return invoice_data['last_invoice']


def func_send_invoice(order_number, clients=None, items=None):
    db = get_db()
    collection = db['orders']

    order = collection.find_one({"order_number": order_number})
    if not order:
        return jsonify({"message": f"No se encontró la orden {order_number}"}), 404

    if clients is None:
        clients = get_all_clients()
    if items is None:
        items = get_all_items()

    identification = order["customer_documentNumber"].split("-")[0]
    client = find_client_by_identification(clients, identification)
    if not client:
        client, error_message = create_client(order, identification)
        if not client:
            return jsonify({"message": f"No se encontró y no se pudo crear el cliente {order['customer_documentNumber']} en Alegra: {error_message}"}), 400
        clients.append(client)

    res = transform_and_send_invoice(order, client, items)
    print(res.text)
    if res.status_code == 201:
        collection.update_one({"order_number": order_number}, {"$set": {"alegra_id": res.json().get("id")}})
    return jsonify({"message": res.text}), res.status_code


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
