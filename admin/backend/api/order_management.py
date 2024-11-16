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
from utils.email_utils import send_new_order
from io import StringIO
import csv
from models.product import Product


order_api = Blueprint('order', __name__)

@order_api.route('/order', methods=['POST'])
@order_api.route('/order/<string:order_number>', methods=['POST'])
def create_order(order_number=None):
    data = request.get_json()
    id = data.get('id', None)
    order_number = data.get('order_number', order_number)
    customer_email = data.get('email') or data.get('customer_email') or ''
    customer_phone = data.get('phoneNumber') or data.get('customer_phone')  or ''
    customer_documentNumber = data.get('documentNumber') or data.get('customer_documentNumber') or ''
    customer_documentType = data.get('documentType') or data.get('customer_documentType') or ''
    customer_name = data.get('customerName') or data.get('customer_name')  or ''
    delivery_date = data.get('deliveryDate') or data.get('delivery_date') or ''
    status = data.get('status') or 'Creada'
    created_at = data.get('created_at', None)
    updated_at = data.get('updated_at', None)
    products = data.get('products', [])
    total = data.get('total', 0.0)
    deliverySlot = data.get('deliverySlot', '09:00-12:00')
    paymentMethod = data.get('paymentMethod', 'Cash')
    deliveryAddress = data.get('deliveryAddress', 'Default Address')
    deliveryAddressDetails = data.get('deliveryAddressDetails') or ''
    deliveryCost = data.get('deliveryCost', 0.0)
    discount = data.get("discount", 0.0)
    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400

    order = Order(      
        id = id,  
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
        deliveryAddressDetails = deliveryAddressDetails,
        deliveryCost = deliveryCost,
        discount=discount
    )
    finded_order = Order.find_by_order_number(order_number=order_number)
    if finded_order:
        order.updated()
    else:
        order.save()
        send_order_email(order_number, customer_email, delivery_date, products, total)
    return jsonify({'message': 'Order created successfully'}), 201
@order_api.route('/order/<string:id>', methods=['DELETE'])
def delete_order(id=None):
    finded_order = Order.object(id)
    finded_order.delete_order()
    return jsonify({'message': 'Order created successfully'}), 201
@order_api.route('/orders/<string:startDate>/<string:endDate>', methods=['GET'])
def list_orders(startDate,endDate):
    orders_cursor = Order.find_by_date(startDate,endDate)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
        "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A")),
        "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType", "N/A")),
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
@order_api.route('/orders/status/<string:status>', methods=['GET'])
def list_ordersByStats(status):
    orders_cursor = Order.find_by_status(status)
    order_data = [
        {
         "id": str(order["_id"]), 
         "order_number": order["order_number"] if order["order_number"] else order["orderNumber"], 
         "customer_email": order["customer_email"] if order["customer_email"] else order["customerEmail"], 
         "customer_phone": order["customer_phone"] if order["customer_phone"] else order["customerPhone"], 
        "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A")),
        "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType", "N/A")),
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

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_path = 'https://buyfrescapp.com/images/banner1.png'
    logo = Image(image_path, width=200, height=70)
    centered_style = ParagraphStyle(
            name='Centered',
            fontSize=16,  # Tamaño de la letra aumentado a 16
            alignment=TA_CENTER,  # Centrado horizontal
            textColor=colors.white,  # Color del texto blanco
            leading=50  # Espaciado entre líneas para centrar verticalmente
        )
    pdf_content = []
    remision_number = order.order_number
    remision_paragraph = Paragraph(
        '<font>Remisión #({}) {}</font>'.format(remision_number, order.delivery_date),
        centered_style
    )

    green_box = Table(
        [[remision_paragraph]],
        colWidths=[250],
        rowHeights=[70],
        style=[('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#97D700'))]
    )

    # Tabla contenedora de la imagen y la caja verde
    content_table = Table([
        [logo, green_box]
    ], colWidths=[200, 250])

    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/>', styles['Normal']))
    table_width = 500

    # Aplicar estilos de WordWrap a las celdas de la tabla
    word_wrap_style = getSampleStyleSheet()["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    # Datos de la orden
    order_data = [
        ['Nombre', Paragraph(order.customer_name, word_wrap_style), 'Teléfono del Cliente', Paragraph(order.customer_phone, word_wrap_style)],
        ['Método de pago', Paragraph(order.paymentMethod, word_wrap_style), 'Horario de entrega', Paragraph(order.deliverySlot, word_wrap_style)],
        ['Dirección de entrega', Paragraph(order.deliveryAddress, word_wrap_style), 'Detalle de entrega', Paragraph(order.deliveryAddressDetails, word_wrap_style)]
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
    for product in list(order.products):
        sku = product['sku']
        name = product['name']
        quantity = product['quantity']
        price_sale = locale.format_string('%.2f', round(product.get('price_sale'),0), grouping=True)
        total = locale.format_string('%.2f', round(float(product.get('price_sale')) * float(quantity),0), grouping=True)
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [sku, name_paragraph, quantity, price_sale, total]
        product_data.append(product_row)

    subtotal = sum(round(float(product['quantity']) * float(product['price_sale']),0) for product in list(order.products))
    try:
        descuentos = float(order.discount)
    except:
        descuentos = 0    
    total = subtotal - descuentos
    subtotal_formatted = locale.format_string('%.2f', subtotal, grouping=True)
    descuentos_formatted = locale.format_string('%.2f', descuentos, grouping=True)
    total_formatted = locale.format_string('%.2f', total, grouping=True)
    image_path_payment = 'https://buyfrescapp.com/images/medio_pago.png'  # URL o ruta local de la imagen del medio de pago
    payment_image = Image(image_path_payment, width=290, height=100)  # Ajustar tamaño de la imagen
    product_data.extend([[payment_image,'','','',''],
        ['', '', '', 'Subtotal', subtotal_formatted],
        ['', '', '', 'Descuentos', descuentos_formatted],
        ['', '', '', 'Total', total_formatted]
    ])


    product_table = Table(product_data, colWidths=[table_width / 5] * 5)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),  # Color de fondo del encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),  # Bordes internos
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),  # Borde externo
        ('SPAN', (0, len(order.products)+1), (2, len(order.products)+4))

    ]))
    pdf_content.append(product_table)

    # Generar el PDF
    pdf.build(pdf_content)

    # Mover el cursor del buffer al inicio
    buffer.seek(0)

    # Crear una respuesta con el archivo PDF y establecer el encabezado Content-Disposition
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=Orden_{}.pdf'.format(remision_number)
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
         "deliveryAddress": order['deliveryAddress'],
         "deliveryAddressDetails" : order['deliveryAddressDetails']
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200

@order_api.route('/orders_latest_customer/<string:email>', methods=['GET'])
def orders_latest_customer(email):
    # Encuentra las órdenes del cliente por su correo electrónico y ordénalas por delivery_date en orden descendente
    orders_cursor = Order.find_by_customer(email).sort("delivery_date", -1).limit(3)
    
    order_data = [
        {
            "id": str(order["_id"]), 
            "order_number": order.get("order_number", order.get("orderNumber")), 
            "customer_email": order.get("customer_email", order.get("customerEmail")), 
            "customer_phone": order.get("customer_phone", order.get("customerPhone")), 
            "customer_documentNumber": order.get("customer_documentNumber", order.get("customerDocumentNumber")), 
            "customer_documentType": order.get("customer_documentType", order.get("customerDocumentType")), 
            "customer_name": order.get("customer_name", order.get("customerName")), 
            "delivery_date": order.get("delivery_date", order.get("deliveryDate")), 
            "status": order["status"], 
            "created_at": order["created_at"], 
            "updated_at": order["updated_at"], 
            "products": order["products"],
            "total": order["total"], 
            "deliverySlot": order["deliverySlot"], 
            "paymentMethod": order["paymentMethod"], 
            "deliveryAddress": order['deliveryAddress'],
            "deliveryAddressDetails": order['deliveryAddressDetails']
        }
        for order in orders_cursor
    ]
    
    orders_json = json.dumps(order_data)
    return orders_json, 200


def send_order_email(order_number, customer_email, delivery_date, products, total):
    subject = f'Orden confirmada - Orden #{order_number}'
    orden = Order.find_by_order_number(order_number)
    # Construir la lista de productos en HTML
    product_list_html = ""
    for product in products:
        subtotal = product['quantity'] * float(product['price_sale'])
        price_formatted = f'{float(product["price_sale"]):,.2f}'  
        subtotal_formatted = f'{subtotal:,.2f}'  #
        product_list_html += f"<tr><td>{product['name']}</td><td style='text-align: center;'>{product['quantity']}</td><td style='text-align: center;'>{price_formatted}</td><td style='text-align: center;'>{subtotal_formatted}</td></tr>"
    
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
            style="background-color: #f7f7f7; margin: 0; padding: 70px 0 70px 0; width: 100%; padding-top: 70px; padding-bottom: px; -webkit-text-size-adjust: none; "
            backgound-color="#f7f7f7" width="100%" text-align="center">
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
                                                            src="https://app.buyfrescapp.com:5000/api/shared/banner1.png"
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
                                                style="padding: 36px 48px; text-align: left; background-color: #97D700; color: white; font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5;">
                                                <p style="margin: 0; font-size: 18px; font-weight: bold;">Hola</p>
                                                <p style="margin: 8px 0; font-size: 22px; font-weight: bold;">{orden.customer_name},</p>
                                                <p style="margin: 8px 0;">Hemos recibido tu nueva orden y será entregada el {delivery_date} en {orden.deliveryAddress} entre {orden.deliverySlot}.</p>
                                                <p style="margin: 8px 0;">Será un gusto entregarla. Gracias</p>
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
                                    <p style="text-align: right;"><b>Total: </b>{total:,.2f}</p>
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

@order_api.route('/orders/csv', methods=['GET'])
def download_orders_csv():
    # Obtener todas las órdenes
    orders_cursor = Order.objects()

    # Crear un objeto StringIO para escribir el CSV en memoria
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)

    # Escribir la cabecera del CSV
    csv_writer.writerow([
        "Order ID"
        , "Order Number"
        , "Customer Email"
        , "Customer Phone"
        ,"Customer Document Number"
        , "Customer Document Type"
        , "Customer Name"
        ,"Delivery Date"
        , "Status"
        , "Created At"
        , "Updated At"
        , "Total"
        , "Delivery Slot"
        , "Payment Method"
       , "Delivery Address"
        , "Delivery Address Details"
        ,"Product SKU"
        , "Product Name"
        , "Product Description"
        , "Product Quantity"
        ,"Product Price Sale"
        , "Product Price Purchase"
        , "Product Category"
        , "Product Root"
        , "Product Child"
        , "Product Discount"
        , "Product Margen"
        , "Product IVA"
        , "Product IVA Value"
        , "Product Status"
        , "Product Proveedor"
        , "Product Step Unit"
    ])

    # Escribir los datos de las órdenes y productos
    for order in orders_cursor:
        order_id = str(order["_id"])
        order_number = order["order_number"] if order["order_number"] else order["orderNumber"]
        customer_email = order["customer_email"] if order["customer_email"] else order["customerEmail"]
        customer_phone = order["customer_phone"] if order["customer_phone"] else order["customerPhone"]
        customer_document_number = order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A"))
        customer_document_type = order.get("customer_documentType", order.get("customerDocumentType", "N/A"))
        customer_name = order["customer_name"] if order["customer_name"] else order["customerName"]
        delivery_date = order["delivery_date"] if order["delivery_date"] else order["deliveryDate"]
        status = order["status"]
        created_at = order["created_at"]
        updated_at = order["updated_at"]
        total = order["total"]
        delivery_slot = order["deliverySlot"]
        payment_method = order["paymentMethod"]
        delivery_address = order["deliveryAddress"]
        delivery_address_details = order["deliveryAddressDetails"]

        for product in order["products"]:
            product_sku = product.get("sku", "")
            product_quantity = product.get("quantity", "")
            product_price_sale = product.get("price_sale", "")
            
            # Buscar el producto en la colección de productos usando el SKU
            product_data = Product.find_by_sku(sku=product_sku)
            if product_data:
                product_name = product_data["name"]
                product_description = product_data["description"]
                product_price_purchase = product_data["price_purchase"]
                product_category = product_data["category"]
                product_root = product_data["root"]
                product_child = product_data["child"]
                product_discount = product_data["discount"]
                product_margen = product_data["margen"]
                product_iva = product_data["iva"]
                product_iva_value = product_data["iva_value"]
                product_status = product_data["status"]
                product_proveedor = product_data["proveedor"]
                product_step_unit = product_data["step_unit"]
            else:
                product_name = "Unknown"
                product_description = "Unknown"
                product_price_purchase = "N/A"
                product_category = "N/A"
                product_root = "N/A"
                product_child = "N/A"
                product_discount = "N/A"
                product_margen = "N/A"
                product_iva = "N/A"
                product_iva_value = "N/A"
                product_status = "N/A"
                product_proveedor = "N/A"
                product_step_unit = "N/A"

            csv_writer.writerow([
                order_id
                , order_number
                , customer_email
                , customer_phone
                , customer_document_number
                , customer_document_type
                , customer_name
                , delivery_date
                , status
                , created_at
                , updated_at
                , total
                , delivery_slot
                , payment_method
                , delivery_address
                , delivery_address_details
                , product_sku
                , product_name
                , product_description
                , product_quantity
                , product_price_sale
                , product_price_purchase
                , product_category
                , product_root
                , product_child
                , product_discount
                , product_margen
                , product_iva
                , product_iva_value
                , product_status
                , product_proveedor
                , product_step_unit                
            ])

    csv_file.seek(0)

    # Crear una respuesta y añadir los headers adecuados
    response = Response(csv_file.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'inline; filename=orders.csv'
    return response

