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
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
report_api = Blueprint('report', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
orders_collection = db['orders']  
products_collection = db['orders']  
@report_api.route('/picking/<string:date>', methods=['GET'])
def get_picking(date):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_path = 'http://app.buyfrescapp.com:5000/api/shared/banner1.png'
    logo = Image(image_path, width=200, height=70)
    centered_style = ParagraphStyle(
            name='Centered',
            fontSize=16,  # Tamaño de la letra aumentado a 16
            alignment=TA_CENTER,  # Centrado horizontal
            textColor=colors.white,  # Color del texto blanco
            leading=50  # Espaciado entre líneas para centrar verticalmente
        )
    pdf_content = []
    orders = orders_collection.find({"delivery_date" : date})
    for order in orders:
        if not order:
            return jsonify({'message': 'Order not found'}), 404        
        remision_number = order['order_number']
        remision_paragraph = Paragraph('<font>Remisión de la orden # {}</font>'.format(remision_number), centered_style)
        green_box = Table([[remision_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#97D700'))])

        # Tabla contenedora de la imagen y la caja verde
        content_table = Table([
            [logo, green_box]
        ], colWidths=[200, 250])
        pdf_content.append(content_table)
        pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
        table_width = 500

        # Aplicar estilos de WordWrap a las celdas de la tabla
        word_wrap_style = getSampleStyleSheet()["Normal"]
        word_wrap_style.wordWrap = 'CJK'

        # Datos de la orden
        order_data = [
            ['Nombre', Paragraph(order['customer_name'], word_wrap_style), 'Teléfono del Cliente', Paragraph(order['customer_phone'], word_wrap_style)],
            ['Método de pago', Paragraph(order['paymentMethod'], word_wrap_style), 'Horario de entrega', Paragraph(order['deliverySlot'], word_wrap_style)],
            ['Dirección de entrega', Paragraph(order['deliveryAddress'], word_wrap_style), 'Detalle de entrega', Paragraph(order['deliveryAddressDetails'], word_wrap_style)]
        ]

        # Crear la tabla con cuatro columnas
        order_table = Table(order_data, colWidths=[table_width / 4] * 4)

        # Aplicar estilos a la tabla
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Color de fondo de las celdas
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),  # Color del texto
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Alinear texto a la izquierda
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Añadir bordes internos a las celdas
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black)  # Añadir borde alrededor de la tabla
        ]))

        # Agregar la tabla al contenido del PDF
        pdf_content.append(order_table)
        pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))

        # Aplicar estilos de WordWrap
        word_wrap_style = styles["Normal"]
        word_wrap_style.wordWrap = 'CJK'

        product_data = [
            ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total'],  # Encabezado
        ]
        for product in list(order['products']):
            sku = product['sku']
            name = product['name']
            quantity = product['quantity']
            price_sale = locale.format_string('%.2f', round(product.get('price_sale'),0), grouping=True)
            total = locale.format_string('%.2f', round(float(product.get('price_sale')) * float(quantity),0), grouping=True)
            name_paragraph = Paragraph(name, word_wrap_style)
            product_row = [sku, name_paragraph, quantity, price_sale, total]
            product_data.append(product_row)

        subtotal = sum(round(float(product['quantity']) * float(product['price_sale']),0) for product in list(order['products']))
        descuentos = 0
        total = subtotal - descuentos
        subtotal_formatted = locale.format_string('%.2f', subtotal, grouping=True)
        descuentos_formatted = locale.format_string('%.2f', descuentos, grouping=True)
        total_formatted = locale.format_string('%.2f', total, grouping=True)
        product_data.extend([['','','','',''],
            ['', '', '', 'Subtotal', subtotal_formatted],
            ['', '', '', 'Descuentos', descuentos_formatted],
            ['', '', '', 'Total', total_formatted]
        ])
        product_table = Table(product_data, colWidths=[table_width / 5] * 5)
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Añadir bordes internos a las celdas
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black)  # Añadir borde alrededor de la tabla
        ]))
        pdf_content.append(product_table)
        pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=remisiones_{}_{}.pdf'.format(date,date)
    return response

@report_api.route('/compras/<string:date>/<string:supplier>', methods=['GET'])
def get_compras(date,supplier):
    pipeline = [
        {
            "$match": {
                "delivery_date": date
            }
        },
        {
            "$unwind": "$products"
        },
        {
            "$group": {
                "_id": "$products.sku",
                "total_quantity_ordered": {"$sum": "$products.quantity"}
            }
        },
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "sku",
                "as": "product_info"
            }
        },
        {
            "$unwind": "$product_info"
        },
        {
            "$project": {
                "_id": 0,
                "sku": "$_id",
                "name": "$product_info.name",
                "total_quantity_ordered": 1,
                "price_purchase": "$product_info.price_purchase",
                "proveedor": "$product_info.proveedor",
                "category": "$product_info.category"
            }
        }
    ]
    if supplier != 'Todos':
        pipeline.append({
            "$match": {
                "proveedor": supplier
            }
        })
    pipeline.append({
        "$sort": {
            "category": 1  # Orden ascendente por categoría
        }
    })
    products = list(orders_collection.aggregate(pipeline))
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_path = 'http://app.buyfrescapp.com:5000/api/shared/banner1.png'
    logo = Image(image_path, width=200, height=70)
    centered_style = ParagraphStyle(
            name='Centered',
            fontSize=16,  # Tamaño de la letra aumentado a 16
            alignment=TA_CENTER,  # Centrado horizontal
            textColor=colors.white,  # Color del texto blanco
            leading=50  # Espaciado entre líneas para centrar verticalmente
        )
    pdf_content = []
    compras_paragraph = Paragraph('<font>Compras para el {}</font>'.format(date), centered_style)
    green_box = Table([[compras_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#97D700'))])
    content_table = Table([
    [logo, green_box]], colWidths=[200, 250])
    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    table_width = 500
    product_data = [
        ['sku', 'Nombre', 'Categoria', 'Cantidad', 'Precio Unitario', 'Proveedor'],  # Encabezado
    ]
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'
    for product in products:
        sku = product['sku']
        name = product['name']
        quantity = product.get('total_quantity_ordered')
        price = locale.format_string('%.2f', round(product.get('price_purchase'),0), grouping=True)
        proveedor = product['proveedor']
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [sku, name_paragraph, product.get('category'), quantity, price, proveedor]
        product_data.append(product_row)
    total = locale.format_string('%.2f',sum(round(float(product['total_quantity_ordered']) * float(product['price_purchase']),0) for product in products), grouping=True)
    product_data.extend([['','','','',''],
            ['', '', 'Total', total, '']
        ])
    product_table = Table(product_data, colWidths=[table_width / 6] * 6)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Añadir bordes internos a las celdas
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)  # Añadir borde alrededor de la tabla
    ]))
    pdf_content.append(product_table)
    pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=ordenes_{}.pdf'.format(date)
    return response