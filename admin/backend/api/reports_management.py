from flask import Blueprint, jsonify, request, send_file, Response
from models.order import Order
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import locale
from flask import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from io import BytesIO
from utils.email_utils import send_new_order  # Importa la función send_email que creamos antes
from pymongo import MongoClient


report_api = Blueprint('report', __name__)
client = MongoClient('mongodb://admin:Caremonda@3.23.102.32:27017/frescapp') 
db = client['frescapp']
orders_collection = db['orders']  

@report_api.route('/picking/<string:date>', methods=['GET'])
def get_picking(date):
    orders = orders_collection.find({"delivery_date" : date})

    if not orders:
        return jsonify({'message': 'No orders found for the specified date'}), 404

    # Crear un objeto de tipo BytesIO para almacenar el PDF en memoria
    buffer = BytesIO()

    # Establecer el locale para formatear los números
    locale.setlocale(locale.LC_ALL, '')

    # Crear un documento PDF
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilos de párrafo
    styles = getSampleStyleSheet()

    # Crear contenido del PDF
    pdf_content = []

    # Agregar encabezado
    logo_path = 'http://3.23.102.32:5000/api/shared/banner1.png'
    logo = Image(logo_path, width=500, height=170)
    pdf_content.append(logo)

    # Agregar título
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#97D700'),
        spaceAfter=0.5  
    )
    title_text = '<font size="20">Ordenes para la fecha {}</font>'.format(date)
    title = Paragraph(title_text, title_style)
    pdf_content.append(title)

    # Agregar tabla de órdenes
    order_data = [
        ['Número de Orden', 'Email del Cliente', 'Teléfono del Cliente']
    ]
    for order in orders:
        order_data.append([order.order_number, order.customer_email, order.customer_phone])
    order_table = Table(order_data, colWidths=[1.5 ] * 3) 
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
    ]))
    pdf_content.append(order_table)

    # Agregar espacio entre la tabla de órdenes y la tabla de productos
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))

    # Agregar tabla de productos para cada orden
    for order in orders:
        product_data = [
            ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total']
        ]
        for product in order.products:
            sku = product.sku
            name = product.name
            quantity = product.quantity
            price_sale = locale.format_string('%.2f', product.price_sale, grouping=True)
            total = locale.format_string('%.2f', product.quantity * product.price_sale, grouping=True)
            product_data.append([sku, name, quantity, price_sale, total])
        product_table = Table(product_data, colWidths=[1.0 ] * 5) # type: ignore
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
        ]))
        pdf_content.append(product_table)

        # Agregar espacio entre las tablas de productos
        pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))

    # Construir el PDF
    pdf.build(pdf_content)

    # Mover el cursor del buffer al inicio
    buffer.seek(0)

    # Crear una respuesta con el archivo PDF y establecer el encabezado Content-Disposition
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=ordenes_{}.pdf'.format(date)

    return response