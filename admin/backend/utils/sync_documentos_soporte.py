from flask import Blueprint, jsonify, request
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
import requests
from pymongo import MongoClient

alegra_api = Blueprint('alegra', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']

# URL base y cabeceras para la API de Alegra
url_contacts = "https://api.alegra.com/api/v1/contacts"
url_items = "https://api.alegra.com/api/v1/items"
url_doc_soportes = "https://api.alegra.com/api/v1/support-documents"
headers = {
    "accept": "application/json",
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"  # Reemplaza esto con tus credenciales
}

# Función para imprimir documentos soportes
def imprimir_documentos_soportes():
    response = requests.get(url_doc_soportes, headers=headers)
    
    if response.status_code == 200:
        documentos = response.json()
        print(json.dumps(documentos, indent=4))
    else:
        print(f"Error: {response.status_code}")

# Llamar la función
imprimir_documentos_soportes()
