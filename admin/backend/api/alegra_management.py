from flask import Blueprint, jsonify, request
from models.customer import Customer
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
import utils.email_utils as emails
import requests
from datetime import datetime
from pymongo import MongoClient

alegra_api = Blueprint('alegra', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']

# URL base y cabeceras para la API de Alegra
url_clients = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"
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

    items_data = []
    for product in order["products"]:
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
        "status": "draft",
        "client": client_data,
        "numberTemplate": {
            "id": "16",
            "prefix": "FRES",
            "number": order["order_number"],
            "text": "Autorización de numeración de facturación N°18764069939613 de 2024-04-30 Modalidad Factura Electrónica Desde N° FRES1100 hasta FRES3500 con vigencia hasta 2026-04-30",
            "documentType": "invoice",
            "fullNumber": f"FRES{order['order_number']}",
            "formattedNumber": order["order_number"],
            "isElectronic": True
        },
        "subtotal": sum(item["price_sale"] * item["quantity"] for item in order["products"]),
        "discount": order["discount"],
        "tax": 0,
        "total": order["total"],
        "totalPaid": order["total"],
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
            "amount": order["total"],
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
            "legalStatus": "STAMPED_AND_ACCEPTED_WITH_OBSERVATIONS",
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
    response = requests.post(url_invoice, headers=headers, json=invoice_data)
    if response.status_code == 201:
        print(f"Factura creada exitosamente")
    else:
        print(f"Error al crear la factura: {response.status_code} - {response.text}")

@alegra_api.route('/send_invoice/<string:order_number>', methods=['GET'])
def send_invoice(order_number):
    order = collection.find_one({"order_number": order_number})
    if order:
        clients = get_all_clients()
        items = get_all_items()
        client = find_client_by_identification(clients, order["customer_documentNumber"])
        if client:
            transform_and_send_invoice(order, client, items)
            return jsonify({"message" : f"Orden sincronizada {order_number}"}), 200
        else:
            return jsonify({"message" :f"No se encontró un cliente con identificación {order['customer_documentNumber']}"}), 400

    else:
        return jsonify({"message" : f"No se encontró la orden con número {order_number}"}), 400
