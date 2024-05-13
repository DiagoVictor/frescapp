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


order_api = Blueprint('order', __name__)

@order_api.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('email') if data.get('email') else data.get('customer_email')
    customer_phone = data.get('phoneNumber') if data.get('phoneNumber') else data.get('customer_phone')
    customer_documentNumber = data.get('documentNumber') if data.get('documentNumber') else data.get('customer_documentNumber')
    customer_documentType = data.get('documentType') if data.get('documentType') else data.get('customer_documentType')
    customer_name = data.get('customerName') if data.get('customerName') else data.get('customer_name')
    delivery_date = data.get('deliveryDate') if data.get('deliveryDate') else data.get('delivery_date')
    status = data.get('status') or 'Creada'
    created_at = data.get('created_at')  
    updated_at = data.get('updated_at')  
    products = data.get('products')
    total = data.get('total')
    deliverySlot = data.get('deliverySlot')
    paymentMethod = data.get('paymentMethod')
    deliveryAddress = data.get('deliveryAddress') # Nuevo campo: Dirección de entrega
    deliveryAddressDetails = data.get('deliveryAddressDetails') # Nuevo campo: Detalle dirección

    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400

    if Order.find_by_order_number(order_number=order_number):
        return jsonify({'message': 'Order already exists'}), 400

    order = Order(        
        order_number = order_number,
        customer_email = customer_email,
        customer_phone = customer_phone,
        customer_documentNumber = customer_documentNumber,
        customer_documentType = customer_documentType,
        customer_name = customer_name,
        delivery_date = delivery_date,
        status = status,
        created_at = created_at,
        updated_at = updated_at,
        products = products,
        total = total,
        deliverySlot = deliverySlot,
        paymentMethod = paymentMethod,
        deliveryAddress = deliveryAddress,
        deliveryAddressDetails = deliveryAddressDetails 
    )
    order.save()
    send_order_email(order_number, customer_email, delivery_date, products, total)
    return jsonify({'message': 'Order created successfully'}), 201

# Ruta para actualizar un usuario existente
@order_api.route('/order/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    order_number = data.get('order_number')
    customer_email = data.get('email')
    customer_phone = data.get('phoneNumber')
    customer_documentNumber = data.get('documentNumber')
    customer_documentType = data.get('documentType')
    customer_name = data.get('customerName')
    delivery_date = data.get('deliveryDate')
    status = data.get('status')  
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    products = data.get('products')
    total = data.get('total')
    deliverySlot = data.get('deliverySlot')
    paymentMethod = data.get('paymentMethod')
    deliveryAddress = data.get('deliveryAddress') 
    deliveryAddressDetails = data.get('deliveryAddressDetails') 
    
    order = Order.object(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    order.id = order_id
    order.order_number = order_number or order.order_number
    order.customer_email = customer_email or order.customer_email
    order.customer_phone = customer_phone or order.customer_phone
    order.customer_documentNumber = customer_documentNumber or order.customer_documentNumber
    order.customer_documentType = customer_documentType or order.customer_documentType
    order.customer_name = customer_name or order.customer_name
    order.delivery_date = delivery_date or order.delivery_date
    order.status =status or order.status
    order.created_at = created_at or order.created_at
    order.updated_at = updated_at or order.updated_at
    order.products = products or order.products
    order.total = total or order.total
    order.deliverySlot = deliverySlot or order.deliverySlot
    order.paymentMethod = paymentMethod or order.paymentMethod
    order.deliveryAddress = deliveryAddress or order.deliveryAddress 
    order.deliveryAddressDetails = deliveryAddressDetails or order.deliveryAddressDetails 
    order.updated()
    return jsonify({'message': 'Order updated successfully'}), 200

@order_api.route('/orders', methods=['GET'])
def list_orders():
    orders_cursor = Order.objects()
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
         "customer_documentNumber": order["customer_documentNumber"] if order["customer_documentNumber"] else order["customerDocumentNumber"], 
         "customer_documentType": order["customer_documentType"] if order["customer_documentType"] else order["customerDocumentType"], 
         "customer_name": order["customer_name"] if order["customer_name"] else order["customerName"], 
         "delivery_date": order["delivery_date"] if order["delivery_date"] else order["deliveryDate"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"],
         "deliveryAddress": order["deliveryAddress"], # Nuevo campo: Dirección de entrega
         "deliveryAddressDetails": order["deliveryAddressDetails"]  # Nuevo campo: Detalle dirección
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200

@order_api.route('/generate_pdf/<string:id_order>', methods=['GET'])
def generate_remision(id_order):
    order = Order.object(id_order)

    if not order:
        return jsonify({'message': 'Order not found'}), 404

    # Crear un objeto de tipo BytesIO para almacenar el PDF en memoria
    buffer = BytesIO()

    # Crear un documento PDF
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilos de párrafo
    styles = getSampleStyleSheet()

    # Agregar imagen en la parte superior
    image_path = 'http://3.23.102.32:5000/api/shared/banner1.png'  # Ruta de la imagen
    logo = Image(image_path, width=500, height=170)
    pdf_content = [logo]
    centered_style = ParagraphStyle(
        name='Centered',
        fontSize=16,  # Tamaño de la letra aumentado a 16
        alignment=TA_CENTER,  # Centrado horizontal
        textColor=colors.white,  # Color del texto blanco
        leading=50  # Espaciado entre líneas para centrar verticalmente
    )

    # Crear el párrafo con el nuevo estilo
    remision_number = order.order_number
    remision_paragraph = Paragraph('<font>Remisión de la orden # {}</font>'.format(remision_number), centered_style)

    # Crear la tabla con el párrafo centrado y con el tamaño de letra aumentado
    green_box = Table([[remision_paragraph]], colWidths=[500], rowHeights=[70], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#97D700'))])
    pdf_content.append(green_box)

    # Espacio entre la caja verde y la tabla
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))

    table_width = 500
    order_data = [
        ['Número de Orden', 'Email del Cliente', 'Teléfono del Cliente'],  # Encabezado
        [order.order_number, order.customer_email, order.customer_phone]  # Datos de la orden
    ]
    order_table = Table(order_data, colWidths=[table_width / 3] * 3)  # Dividir el ancho en 3 columnas iguales
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)   # Color del texto del encabezado
    ]))
    pdf_content.append(order_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    styles = getSampleStyleSheet()
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    # Crear tabla con los datos de los productos
    product_data = [
        ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total'],  # Encabezado
    ]
    for product in order.products:
        sku = product.get('sku')
        name = product.get('name')
        quantity = product.get('quantity')
        price_sale = locale.format_string('%.2f', round(product.get('price_sale'),0), grouping=True)
        total = locale.format_string('%.2f', round(float(price_sale) * float(quantity),0), grouping=True)
        
        # Crear un párrafo con el nombre del producto y aplicar el estilo WordWrap
        name_paragraph = Paragraph(name, word_wrap_style)

        product_row = [sku, name_paragraph, quantity, price_sale, total]
        product_data.append(product_row)

    # Agregar líneas adicionales para subtotal, descuentos y total
    subtotal = sum(round(float(product['quantity']) * float(product['price_sale']),0) for product in order.products)
    descuentos = 0  # Ajusta esto según corresponda
    total = subtotal - descuentos
    subtotal_formatted = locale.format_string('%.2f', subtotal, grouping=True)
    descuentos_formatted = locale.format_string('%.2f', descuentos, grouping=True)
    total_formatted = locale.format_string('%.2f', total, grouping=True)
    # Añadir líneas adicionales al producto_data
    product_data.extend([
        ['', '', '', 'Subtotal', subtotal_formatted],
        ['', '', '', 'Descuentos', descuentos_formatted],
        ['', '', '', 'Total', total_formatted]
    ])

    # Crear la tabla de productos
    product_table = Table(product_data, colWidths=[table_width / 5] * 5)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)   # Color del texto del encabezado
    ]))
    pdf_content.append(product_table)

    # Generar el PDF
    pdf.build(pdf_content)

    # Mover el cursor del buffer al inicio
    buffer.seek(0)

    # Crear una respuesta con el archivo PDF y establecer el encabezado Content-Disposition
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=orden_{}.pdf'.format(order.order_number)

    return response

@order_api.route('/orders_customer/<string:email>', methods=['GET'])
def list_orders_customer(email):
    orders_cursor = Order.find_by_customer(email)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
         "customer_documentNumber": order["customer_documentNumber"] if order["customer_documentNumber"] else order["customerDocumentNumber"], 
         "customer_documentType": order["customer_documentType"] if order["customer_documentType"] else order["customerDocumentType"], 
         "customer_name": order["customer_name"] if order["customer_name"] else order["customerName"], 
         "delivery_date": order["delivery_date"] if order["delivery_date"] else order["deliveryDate"], 
         "status": order["status"], 
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"], 
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200

def send_order_email(order_number, customer_email, delivery_date, products, total):
    subject = f'Orden confirmada - Orden #{order_number}'
    
    # Construir la lista de productos en HTML
    product_list_html = ""
    for product in products:
        subtotal = product['quantity'] * product['price_sale']
        price_formatted = f'{subtotal:,.2f} COP'  # Formatear el precio con COP
        product_list_html += f"<tr><td>{product['name']}</td><td style='text-align: center;'>{product['quantity']}</td><td style='text-align: center;'>{price_formatted}</td><td style='text-align: center;'>{subtotal:,.2f} COP</td></tr>"
    
    # Construir el mensaje HTML completo
    html_message = f"""
    <!DOCTYPE html>
    <html lang="es" style="height: 100%; position: relative;" height="100%">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta content="width=device-width, initial-scale=1.0" name="viewport">
        <title>Frescapp</title>
    </head>
    <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0"
        class="kt-woo-wrap order-items-normal k-responsive-normal title-style-none email-id-new_order"
        style="height: 100%; position: relative; background-color: #f7f7f7; margin: 0; padding: 0;" height="100%"
        backgound-color="#f7f7f7">
        <div id="wrapper" dir="ltr"
            style="background-color: #f7f7f7; margin: 0; padding: 70px 0 70px 0; width: 100%; padding-top: 70px; padding-bottom: px; -webkit-text-size-adjust: none;"
            backgound-color="#f7f7f7" width="100%">
            <table cellpadding="0" cellspacing="0" height="100%" width="100%">
                <tr>
                    <td text-align="center" vtext-align="top">
                        <table id="template_header_image_container" style="width: 100%; background-color: transparent;"
                            width="100%" backgound-color="transparent">
                            <tr id="template_header_image">
                                <td text-align="center" vtext-align="middle">
                                    <table cellpadding="0" cellspacing="0" width="100%" id="template_header_image_table">
                                        <tr>
                                            <td text-align="center" vtext-align="middle"
                                                style="text-text-align: center; padding-top: 0px; padding-bottom: 0px;">
                                                <p style="margin-bottom: 0; margin-top: 0;"><a
                                                        href="https://www.buyfrescapp.com" target="_blank"
                                                        style="font-weight: normal; color: #97d700; display: block; text-decoration: none;"><img
                                                            src="https://www.buyfrescapp.com/wp-content/uploads/2024/03/cropped-Captura-de-pantalla-2024-03-14-132748-1.png"
                                                            alt="Frescapp" width="600"
                                                            style="border: none; display: inline; font-weight: bold; height: auto; outline: none; text-decoration: none; text-transform: capitalize; font-size: 14px; line-height: 24px; max-width: 100%; width: 600px;"></a>
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                        <table cellpadding="0" cellspacing="0" width="600" id="template_container"
                            style="background-color: #fff; overflow: hidden; border-style: solid; border-width: 1px; border-right-width: px; border-bottom-width: px; border-left-width: px; border-color: #dedede; border-radius: 3px; box-shadow: 0 1px 4px 1px rgba(0,0,0,.1);"
                            backgound-color="#fff">
                            <tr>
                                <td text-align="center" vtext-align="top">
                                    <!-- Header -->
                                    <table cellpadding="0" cellspacing="0" width="100%" id="template_header"
                                        style='border-bottom: 0; font-weight: bold; line-height: 100%; vertical-text-align: middle; font-family: "Helvetica Neue",Helvetica,Roboto,Arial,sans-serif; background-color: #97d700; color: #fff;'
                                        backgound-color="#97d700">
                                        <tr>
                                            <td id="header_wrapper"
                                                style="padding: 36px 48px; display: block; text-text-align: left; padding-top: px; padding-bottom: px; padding-left: 48px; padding-right: 48px;"
                                                text-align="left">
                                            <h1> Hemos recibido tu nueva orden, será un gusto entregarla.
                                            </td>
                                        </tr>
                                    </table>
                                    <!-- End Header -->
                                    <!-- Products List -->
                                    <table cellpadding="0" cellspacing="0" width="100%" id="template_product_list"
                                        style="font-family: 'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif; font-size: 14px; line-height: 24px; color: #333; width: 100%;"
                                        backgound-color="#ffffff">
                                        <tr>
                                            <th>Producto</th>
                                            <th style="text-align: center;">Cantidad</th>
                                            <th style="text-align: center;">Precio Unitario</th>
                                            <th style="text-align: center;">Subtotal</th>
                                        </tr>
                                        {product_list_html}
                                    </table>
                                    <!-- End Products List -->
                                    <!-- Total -->
                                    <p style="text-align: right;">Total: {total:,.2f} COP</p>
                                    <!-- End Total -->
                                </td>
                            </tr>
                        </table> <!-- End template container -->
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """
    
    # Envía el correo
    send_new_order(subject, html_message, customer_email)
