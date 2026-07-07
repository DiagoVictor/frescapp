from flask import Blueprint, jsonify, request, current_app
from ..models.customer import Customer
from flask_bcrypt import Bcrypt
from datetime import datetime
from ..utils import email_utils as emails
import json

customer_api = Blueprint('customer', __name__)

bcrypt = Bcrypt()

# ======================================================
# 🧩 CREAR NUEVO CLIENTE
# ======================================================
@customer_api.route('/customer', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()

        # Validaciones básicas
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')

        if not phone or not email or not password:
            return jsonify({'message': 'Faltan campos obligatorios (teléfono, email o contraseña).'}), 400

        # Verificar duplicados
        if Customer.find_by_email(email=email):
            return jsonify({'message': 'Correo electrónico ya está asociado a otro cliente.'}), 400

        # Encriptar contraseña
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Crear el cliente
        customer = Customer(
            phone=data.get('phone'),
            name=data.get('name'),
            document=data.get('document'),
            document_type=data.get('document_type'),
            address=data.get('address'),
            restaurant_name=data.get('restaurant_name'),
            email=email,
            status=data.get('status', 'Activo'),
            created_at=data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            updated_at=data.get('updated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            password=hashed_password,
            category=data.get('category', 'General'),
            list_products="",
            role="Cliente",
            user=data.get('user', email)
        )
        customer.save()

        # Enviar correo de bienvenida
        subject = '¡Bienvenido a Frescapp!'
        message = f"""
        <html>
        <body style="font-family: Arial; color: #333;">
            <h2>Hola {customer.name} 👋</h2>
            <p>Desde el equipo de <b>Frescapp</b> te damos la bienvenida a la plataforma que te ayudará 
            a optimizar tus compras y crecer con nosotros 🚀</p>
            <hr>
            <p>Gracias por registrarte en <a href="https://www.buyfrescapp.com">buyfrescapp.com</a></p>
        </body>
        </html>
        """
        emails.send_new_account(subject, message, email)

        return jsonify({'message': 'Customer created successfully.'}), 201

    except Exception as e:
        current_app.logger.error(f"Error creating customer: {e}")
        return jsonify({'error': str(e)}), 500


# ======================================================
# ✏️ ACTUALIZAR CLIENTE EXISTENTE
# ======================================================
@customer_api.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        data = request.get_json()
        customer = Customer.object(customer_id)

        if not customer:
            return jsonify({'message': 'Customer not found'}), 404

        # Actualizar campos solo si se envían
        for field in [
            "phone", "name", "document", "document_type", "address",
            "restaurant_name", "email", "status", "created_at", "updated_at",
            "category", "role"
        ]:
            value = data.get(field)
            if value is not None:
                setattr(customer, field, value)

        customer.updated()
        return jsonify({'message': 'Customer updated successfully.'}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating customer: {e}")
        return jsonify({'error': str(e)}), 500


# ======================================================
# 📋 LISTAR CLIENTES
# ======================================================
@customer_api.route('/customers', methods=['GET'])
def list_customers():
    try:
        customers = Customer.objects({
            "phone": 1, "name": 1, "document": 1, "document_type": 1,
            "address": 1, "restaurant_name": 1, "email": 1, "status": 1,
            "created_at": 1, "updated_at": 1, "category": 1, "list_products": 1,
            "segmentation": 1, "role": 1
        })
        customers_data = [
            {
                "id": str(cust.get("_id", "")),
                "phone": cust.get("phone", ""),
                "name": cust.get("name", ""),
                "document": cust.get("document", ""),
                "document_type": cust.get("document_type", ""),
                "address": cust.get("address", ""),
                "restaurant_name": cust.get("restaurant_name", ""),
                "email": cust.get("email", ""),
                "status": cust.get("status", ""),
                "created_at": cust.get("created_at", ""),
                "updated_at": cust.get("updated_at", ""),
                "category": cust.get("category", ""),
                "list_products": cust.get("list_products", []),
                "segmentation": cust.get("segmentation", ""),
                "role": cust.get("role", "")
            }
            for cust in customers
        ]
        return jsonify(customers_data), 200

    except Exception as e:
        current_app.logger.error(f"Error listing customers: {e}")
        return jsonify({'error': str(e)}), 500


# ======================================================
# 🔍 OBTENER CLIENTE POR ID
# ======================================================
@customer_api.route('/customer/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.object(customer_id)
        if not customer:
            return jsonify({'message': 'Customer not found'}), 404

        customer_json = {
            "phone": customer.phone,
            "name": customer.name,
            "document": customer.document,
            "document_type": customer.document_type,
            "address": customer.address,
            "restaurant_name": customer.restaurant_name,
            "email": customer.email,
            "status": customer.status,
            "created_at": str(customer.created_at),
            "updated_at": str(customer.updated_at),
            "category": customer.category,
            "list_products": customer.list_products
        }
        return jsonify(customer_json), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching customer: {e}")
        return jsonify({'error': str(e)}), 500
