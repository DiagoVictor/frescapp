import io
from flask import Blueprint, jsonify, request, send_file, Response
from ..models.order import Order
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import locale
from flask import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from io import BytesIO
from ..utils.email_utils import send_new_order
from io import StringIO
import csv
from ..models.product import Product
from ..models.customer import Customer
from ..models.route import Route
import os,re
from .product_discount_management import _find_applicable_discount_for_product, compute_final_price


order_api = Blueprint('order', __name__)


@order_api.route('/order', methods=['POST'])
@order_api.route('/order/<string:order_number>', methods=['POST'])
def create_order(order_number=None):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Información del cliente y orden
    id = data.get('id')
    order_number = data.get('order_number', order_number)
    customer_email = data.get('email') or data.get('customer_email') or ''
    customer_phone = data.get('phoneNumber') or data.get('customer_phone') or ''
    customer_documentNumber = data.get('documentNumber') or data.get('customer_documentNumber') or ''
    customer_documentType = data.get('documentType') or data.get('customer_documentType') or ''
    customer_name = data.get('customerName') or data.get('customer_name') or ''
    delivery_date = data.get('deliveryDate') or data.get('delivery_date') or ''
    status = data.get('status') or 'Creada'
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')
    products = data.get('products', [])

    if not customer_email or not delivery_date:
        return jsonify({'message': 'Missing required fields'}), 400

    # Obtener datos del cliente
    customer = Customer.find_by_email(customer_email)
    open_hour_customer = customer.get('open_hour', '') if customer else ''

    # --- Aplicar descuentos activos a cada producto ---
    total = 0.0
    for product in products:
        discount, origin = _find_applicable_discount_for_product(product)
        original_price = float(product.get('price_sale', 0))
        if discount:
            #final_price, _ = compute_final_price(original_price, discount)
            product['price_sale'] = original_price
            product['applied_discount'] = {
                "discount_id": str(discount["_id"]),
                "discount_type": discount.get("discount_type"),
                "value": discount.get("value"),
                "origin": origin
            }
        else:
            product['applied_discount'] = None
        quantity = float(product.get('quantity', 1))
        total += product['price_sale'] * quantity

    # Otros campos de la orden
    paymentMethod = data.get('paymentMethod', 'Cash')
    deliveryAddress = data.get('deliveryAddress', 'Default Address')
    deliveryAddressDetails = data.get('deliveryAddressDetails') or ''
    deliveryCost = data.get('deliveryCost', 0.0)
    discount_value = data.get("discount", 0.0)
    alegra_id = data.get('alegra_id','000')
    deliverySlot = data.get('deliverySlot', '09:00-12:00')
    payment_date = data.get('payment_date', delivery_date)
    driver_name = data.get('driver_name', '')
    seller_name = data.get('seller_name', '')
    source = data.get('source', 'Aplicación')
    totalPayment = 0.0
    status_payment = data.get('status_payment', 'Pendiente') or 'Pendiente'

    # Crear objeto Order
    order = Order(      
        id=id,
        order_number=order_number,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_documentNumber=customer_documentNumber.split('-')[0],
        customer_documentType=customer_documentType,
        customer_name=customer_name.capitalize(),
        delivery_date=delivery_date,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
        products=products,
        total=total,
        deliverySlot=deliverySlot,
        paymentMethod=paymentMethod,
        deliveryAddress=deliveryAddress,
        deliveryAddressDetails=deliveryAddressDetails,
        deliveryCost=deliveryCost,
        discount=discount_value,
        alegra_id=alegra_id,
        open_hour=open_hour_customer,
        payment_date=payment_date,
        driver_name=driver_name,
        seller_name=seller_name,
        source=source,
        totalPayment=totalPayment,
        status_payment=status_payment
    )

    # Guardar o actualizar orden
    existing_order = Order.find_by_order_number(order_number)
    if existing_order:
        order.updated()
    else:
        order.save()
        send_order_email(order_number, customer_email, delivery_date, products, total)

    # Actualizar ruta si existe
    # ruta = Route.find_by_date(delivery_date)
    # if ruta:
    #     for stop in ruta.get('stops', []):
    #         if stop["order_number"] == order_number:
    #             stop["total_charged"] = sum(item['price_sale'] * item.get('quantity',1) for item in products)
    #             stop["total_to_charge"] = sum(item['price_sale'] * item.get('quantity',1) for item in products)
    #             stop["quantity_sku"] = len(products)
    #             stop["payment_method"] = paymentMethod
    #             stop["payment_date"] = payment_date
    #             stop["address"] = deliveryAddress
    #             stop["driver_name"] = driver_name
    #     route_exist = Route(
    #         id=ruta['id'],
    #         route_number=ruta.get('route_number'),
    #         close_date=ruta.get('close_date'),
    #         cost=ruta.get('cost'),
    #         stops=ruta.get('stops')
    #     )
    #     route_exist.update()

    return jsonify({
        'message': 'Order created successfully',
        'total': total,
        'products': products
    }), 200


@order_api.route('/order/<string:id>', methods=['DELETE'])
def delete_order(id=None):
    # Buscar la orden por su ID
    finded_order = Order.object(id)
    if not finded_order:
        return jsonify({'message': 'Order not found'}), 404

    # Buscar la ruta asociada a la fecha de entrega de la orden
    ruta = Route.find_by_date(finded_order.delivery_date)
    if ruta:
        # Filtrar los stops para eliminar el que coincide con el número de orden
        ruta['stops'] = [stop for stop in ruta.get('stops', []) if stop.get("order_number") != finded_order.order_number]

        # Actualizar la ruta en la base de datos
        route_exist = Route(
            id=ruta['id'],
            route_number=ruta.get('route_number'),
            close_date=ruta.get('close_date'),
            cost=ruta.get('cost'),
            stops=ruta.get('stops')
        )
        route_exist.update()

    # Eliminar la orden
    finded_order.delete_order()

    return jsonify({'message': 'Order deleted successfully'}), 200
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
         "status_payment": order.get("status_payment", "Pendiente"),
         "created_at": order["created_at"], 
         "updated_at": order["updated_at"], 
         "products": order["products"],
         "total": order["total"], 
         "deliverySlot": order["deliverySlot"], 
         "paymentMethod": order["paymentMethod"],
         "deliveryAddress": order["deliveryAddress"], 
         "deliveryAddressDetails": order["deliveryAddressDetails"] ,
         "alegra_id" :order["alegra_id"],
         "open_hour" : order["open_hour"],
         "driver_name" : order["driver_name"],
         "seller_name" : order["seller_name"],
         "source" : order["source"],
         "totalPayment" : order["totalPayment"]
         }
        for order in orders_cursor
    ]
    orders_json = json.dumps(order_data)
    return orders_json, 200
@order_api.route('/orders/status/<string:status>', methods=['GET'])
def list_ordersByStats(status):
    orders_cursor = Order.find_by_status_payment(status)
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
         "deliveryAddressDetails": order["deliveryAddressDetails"],
        "alegra_id" :order["alegra_id"],
        "totalPayment" : order["totalPayment"],
        "open_hour" : order["open_hour"],
        "driver_name" : order["driver_name"],
        "seller_name" : order["seller_name"],
        "source" : order["source"]
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
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=28.35,
        rightMargin=28.35,
        topMargin=28.35,
        bottomMargin=28.35
    )

    styles = getSampleStyleSheet()
    image_path = 'https://buyfrescapp.com/images/banner1.png'
    logo = Image(image_path, width=95, height=50)
    pdf_content = []
    remision_number = order.order_number
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    # Datos de la orden
    order_data = [
        [logo, 'Remisión #', order.order_number, 'Fecha', order.delivery_date],
        ['', 'Nombre', Paragraph(order.customer_name, word_wrap_style), 'Teléfono del Cliente', Paragraph(order.customer_phone, word_wrap_style)],
        ['', 'Método de pago', Paragraph(order.paymentMethod, word_wrap_style), 'Horario de entrega', Paragraph(order.deliverySlot + ' (' + order.open_hour + ')', word_wrap_style)],
        ['Dirección de entrega', Paragraph(order.deliveryAddress, word_wrap_style),  'Detalle de entrega', Paragraph(order.deliveryAddressDetails, word_wrap_style),'']
    ]

    order_table = Table(order_data, colWidths=[100, 100, 150, 100, 100])
    order_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (0, 2)),  # Logo 3 filas
        ('VALIGN', (0, 0), (0, 2), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 2), 'CENTER'),
        # Dirección: valor solo en columna 2
        ('SPAN', (1, 3), (1, 3)),

        # Detalle: valor ocupa columnas 4 y 5
        ('SPAN', (3, 3), (4, 3)),


        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    pdf_content.append(order_table)
    pdf_content.append(Spacer(1, 20))
    table_width = 550


    # Aplicar estilos de WordWrap
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    product_data = [
        ['SKU', 'Nombre', 'Cantidad', 'Precio Unitario', 'Total'],  # Encabezado
    ]
    for product in sorted(list(order.products), key=lambda x: x['name']):
        sku = product['sku']
        name = product['name']
        quantity = product['quantity']
        price_sale = locale.format_string('%.2f', round(product.get('price_sale'),0), grouping=True)
        total = locale.format_string('%.2f', round(float(product.get('price_sale')) * float(quantity),0), grouping=True)
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [sku, name_paragraph, str(quantity)  + "  " + str(product.get('unit', '')), price_sale, total]
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


    product_table = Table(product_data, colWidths=[120,200,80,80,80])
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
         "deliveryAddressDetails" : order['deliveryAddressDetails'],
            "alegra_id" :order["alegra_id"]
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
    subject = f'✅ Orden confirmada - #{order_number}'
    orden = Order.find_by_order_number(order_number)

    # Helpers
    def money(x):
        try:
            return f"{float(x):,.2f}"
        except Exception:
            return "0.00"

    # Construir filas de productos en HTML
    product_rows_html = ""
    for p in products:
        qty = int(p.get("quantity", 0) or 0)
        price = float(p.get("finalPrice", 0) or 0)
        subtotal = qty * price

        name = (p.get("name") or "").strip()
        product_rows_html += f"""
        <tr>
          <td style="padding:12px 14px; border-bottom:1px solid #eef2f7; color:#111827;">
            {name}
          </td>
          <td style="padding:12px 14px; border-bottom:1px solid #eef2f7; text-align:center; color:#111827;">
            {qty}
          </td>
          <td style="padding:12px 14px; border-bottom:1px solid #eef2f7; text-align:right; color:#111827;">
            ${money(price)}
          </td>
          <td style="padding:12px 14px; border-bottom:1px solid #eef2f7; text-align:right; font-weight:700; color:#111827;">
            ${money(subtotal)}
          </td>
        </tr>
        """

    customer_name = (getattr(orden, "customer_name", "") or "").strip()
    delivery_address = (getattr(orden, "deliveryAddress", "") or "").strip()
    delivery_slot = (getattr(orden, "deliverySlot", "") or "").strip()

    # Mensaje HTML mejorado
    html_message = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Frescapp - Orden confirmada</title>
</head>

<body style="margin:0; padding:0; background:#f3f4f6; font-family:Arial, Helvetica, sans-serif; color:#111827;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6; padding:28px 12px;">
    <tr>
      <td align="center">

        <!-- Contenedor -->
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:14px; overflow:hidden; box-shadow:0 10px 25px rgba(17,24,39,0.08);">
          
          <!-- Hero / Banner -->
          <tr>
            <td style="background:#97D700;">
              <a href="https://www.buyfrescapp.com" target="_blank" style="display:block; text-decoration:none;">
                <img src="https://app.buyfrescapp.com:5000/api/shared/banner1.png"
                     alt="Frescapp"
                     width="600"
                     style="display:block; width:100%; max-width:600px; height:auto; border:0;" />
              </a>
            </td>
          </tr>

          <!-- Encabezado -->
          <tr>
            <td style="padding:26px 28px 10px 28px;">
              <div style="font-size:12px; letter-spacing:1px; text-transform:uppercase; color:#6b7280;">
                Confirmación de compra
              </div>
              <div style="margin-top:6px; font-size:22px; font-weight:800; color:#111827;">
                ¡Tu orden #{order_number} quedó lista! ✅
              </div>

              <div style="margin-top:14px; font-size:14px; line-height:1.6; color:#374151;">
                Hola <b style="color:#111827;">{customer_name}</b>,<br/>
                Recibimos tu pedido y lo estamos preparando con cariño (y sin bugs, o al menos con pocos 😄).
              </div>
            </td>
          </tr>

          <!-- Tarjeta de entrega -->
          <tr>
            <td style="padding:10px 28px 18px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f9fafb; border:1px solid #eef2f7; border-radius:12px;">
                <tr>
                  <td style="padding:14px 14px;">
                    <div style="font-size:14px; font-weight:800; color:#111827; margin-bottom:6px;">
                      📦 Detalles de entrega
                    </div>
                    <div style="font-size:13px; color:#374151; line-height:1.6;">
                      <b>Fecha:</b> {delivery_date}<br/>
                      <b>Dirección:</b> {delivery_address}<br/>
                      <b>Franja:</b> {delivery_slot}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Tabla productos -->
          <tr>
            <td style="padding:0 28px 8px 28px;">
              <div style="font-size:16px; font-weight:800; color:#111827; margin:6px 0 10px;">
                🧾 Resumen del pedido
              </div>

              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #eef2f7; border-radius:12px; overflow:hidden;">
                <tr style="background:#111827;">
                  <th align="left" style="padding:12px 14px; font-size:12px; letter-spacing:.5px; text-transform:uppercase; color:#ffffff;">
                    Producto
                  </th>
                  <th align="center" style="padding:12px 14px; font-size:12px; letter-spacing:.5px; text-transform:uppercase; color:#ffffff;">
                    Cant.
                  </th>
                  <th align="right" style="padding:12px 14px; font-size:12px; letter-spacing:.5px; text-transform:uppercase; color:#ffffff;">
                    Precio
                  </th>
                  <th align="right" style="padding:12px 14px; font-size:12px; letter-spacing:.5px; text-transform:uppercase; color:#ffffff;">
                    Subtotal
                  </th>
                </tr>

                {product_rows_html}
              </table>
            </td>
          </tr>

          <!-- Total -->
          <tr>
            <td style="padding:10px 28px 22px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="left" style="font-size:13px; color:#6b7280;">
                    Si necesitas ajustes, respóndenos este correo.
                  </td>
                  <td align="right" style="font-size:16px; font-weight:900; color:#111827;">
                    Total: <span style="color:#16a34a;">${money(total)}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding:0 28px 26px 28px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#97D700; border-radius:12px;">
                <tr>
                  <td style="padding:14px 16px; color:#0b1f00; font-size:13px; line-height:1.6;">
                    <b>Gracias por comprar con Frescapp.</b><br/>
                    Estamos listos para llevarte frescura de verdad. 🌿
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:18px 28px; background:#f9fafb; border-top:1px solid #eef2f7;">
              <div style="font-size:12px; color:#6b7280; line-height:1.6;">
                <b>Frescapp</b> · www.buyfrescapp.com<br/>
                Soporte: responde a este correo<br/>
                <span style="color:#9ca3af;">Este mensaje fue generado automáticamente para confirmar tu orden.</span>
              </div>
            </td>
          </tr>

        </table>
        <!-- Fin contenedor -->

      </td>
    </tr>
  </table>
</body>
</html>
    """

    send_new_order(subject, html_message, customer_email)

@order_api.route('/orders/csv', methods=['GET'])
def download_orders_csv():
    orders_cursor = Order.objects()
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)

    # Cabecera
    csv_writer.writerow([
        "Order ID", "Order Number", "Customer Email", "Customer Phone",
        "Customer Document Number", "Customer Document Type", "Customer Name",
        "Delivery Date", "Status", "Created At", "Updated At", "Total",
        "Delivery Slot", "Payment Method", "Delivery Address", "Delivery Address Details",
        "Product SKU", "Product Name", "Product Description", "Product Quantity",
        "Product Price Sale", "Product Price Purchase", "Product Category", "Product Root",
        "Product Child", "Product Discount", "Product Applied Discount",
        "Product Margen", "Product IVA", "Product IVA Value", "Product Status",
        "Product Proveedor", "Product Step Unit"
    ])

    for order in orders_cursor:
        order_id = str(order["_id"])
        order_number = order.get("order_number") or order.get("orderNumber")
        customer_email = order.get("customer_email") or order.get("customerEmail")
        customer_phone = order.get("customer_phone") or order.get("customerPhone")
        customer_document_number = order.get("customer_documentNumber", order.get("customerDocumentNumber", "N/A"))
        customer_document_type = order.get("customer_documentType", order.get("customerDocumentType", "N/A"))
        customer_name = order.get("customer_name") or order.get("customerName")
        delivery_date = order.get("delivery_date") or order.get("deliveryDate")
        status = order.get("status")
        created_at = order.get("created_at")
        updated_at = order.get("updated_at")
        total = order.get("total")
        delivery_slot = order.get("deliverySlot")
        payment_method = order.get("paymentMethod")
        delivery_address = order.get("deliveryAddress")
        delivery_address_details = order.get("deliveryAddressDetails")

        for product in order["products"]:
            product_sku = product.get("sku", "")
            product_quantity = product.get("quantity", 1)
            product_price_sale = float(product.get('price_sale', 0))
            applied_discount = product.get('applied_discount', None)

            # Datos del producto desde la colección
            product_data = Product.find_by_sku(sku=product_sku) or {}
            product_name = product_data.get("name", "Unknown")
            product_description = product_data.get("description", "Unknown")
            product_price_purchase = product_data.get("price_purchase", 0)
            product_category = product_data.get("category", "N/A")
            product_root = product_data.get("root", "N/A")
            product_child = product_data.get("child", "N/A")
            product_discount = product_data.get("discount", 0)
            product_margen = product_data.get("margen", 0)
            product_iva = product_data.get("iva", True)
            product_iva_value = product_data.get("iva_value", 0)
            product_status = product_data.get("status", "")
            product_proveedor = product_data.get("proveedor", "")
            product_step_unit = product_data.get("step_unit", 1)

            csv_writer.writerow([
                order_id,
                order_number,
                customer_email,
                customer_phone,
                customer_document_number,
                customer_document_type,
                customer_name,
                delivery_date,
                status,
                created_at,
                updated_at,
                total,
                delivery_slot,
                payment_method,
                delivery_address,
                delivery_address_details,
                product_sku,
                product_name,
                product_description,
                product_quantity,
                product_price_sale,
                product_price_purchase,
                product_category,
                product_root,
                product_child,
                product_discount,
                applied_discount,
                product_margen,
                product_iva,
                product_iva_value,
                product_status,
                product_proveedor,
                product_step_unit
            ])

    csv_file.seek(0)
    response = Response(csv_file.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'inline; filename=orders.csv'
    return response

def limpiar_valor(valor_str):
    """Limpia el valor, eliminando caracteres no numéricos y formatea como float."""
    if not valor_str:
        return 0.0
    # Reemplaza puntos, comas, símbolos y deja solo números y decimales
    valor_str = re.sub(r'[^\d,]', '', valor_str)
    valor_str = valor_str.replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return 0.0


def limpiar_valor(valor_str):
    if not valor_str:
        return 0.0
    valor_str = re.sub(r'[^\d,]', '', valor_str)
    valor_str = valor_str.replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return 0.0
@order_api.route('/order/order_file', methods=['POST'])
def update_order():
    print("Actualizando orden desde CSV")
    try:
        # Validación de archivo CSV
        if 'file' not in request.files or 'data' not in request.form:
            return jsonify({'message': 'Archivo CSV o datos faltantes'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'Archivo no seleccionado'}), 400

        # Parsear JSON con datos de la orden
        data = json.loads(request.form['data'])

        # Leer productos del CSV
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream, delimiter=';')

        productos = []
        total = 0.0

        for row in reader:
            sku = row.get('SKU').strip() if row.get('SKU') else ''
            quantity = limpiar_valor(row.get('CANTIDAD'))
            price = limpiar_valor(row.get('PRECIO'))

            if not sku:
                continue

            product = Product.find_by_sku(sku=sku)
            if not product:
                continue

            product_dict = product
            product_dict['quantity'] = quantity
            product_dict['price_sale'] = price
            productos.append(product_dict)
            total += quantity * price

        # Construir objeto Order
        order = Order(
            id=data.get('id'),
            order_number=data.get('order_number'),
            customer_email=data.get('email') or data.get('customer_email', ''),
            customer_phone=data.get('phoneNumber') or data.get('customer_phone', ''),
            customer_documentNumber=(data.get('documentNumber') or data.get('customer_documentNumber') or '').split('-')[0],
            customer_documentType=data.get('documentType') or data.get('customer_documentType', ''),
            customer_name=(data.get('customerName') or data.get('customer_name', '')).capitalize(),
            delivery_date=data.get('deliveryDate') or data.get('delivery_date', ''),
            status=data.get('status') or 'Creada',
            created_at=data.get('created_at', None),
            updated_at=data.get('updated_at', None),
            products=productos,
            total=total,
            deliverySlot=data.get('deliverySlot', '09:00-12:00'),
            paymentMethod=data.get('paymentMethod', 'Cash'),
            deliveryAddress=data.get('deliveryAddress', 'Default Address'),
            deliveryAddressDetails=data.get('deliveryAddressDetails', ''),
            deliveryCost=data.get('deliveryCost', 0.0),
            discount=data.get("discount", 0.0),
            alegra_id=data.get('alegra_id', '000'),
            open_hour=data.get('open_hour', ''),
            payment_date=data.get('payment_date', data.get('delivery_date')),
            driver_name=data.get('driver_name', ''),
            seller_name=data.get('seller_name', ''),
            source=data.get('source', 'Aplicación'),
            totalPayment=0.0,
            status_payment=data.get('status_payment', 'Pendiente')
        )
        print(order.to_json())
        # Validación mínima
        # if not order.customer_email or not order.delivery_date:
        #     return jsonify({'message': 'Campos requeridos faltantes'}), 400

        # # Verificar existencia
        # existing = Order.find_by_order_number(order.order_number)
        # if existing:
        #     order.updated()
        # else:
        #     order.save()
        #     send_order_email(order.order_number, order.customer_email, order.delivery_date, productos, total)

        return jsonify({'message': 'Orden creada exitosamente'}), 201

    except Exception as e:
        print(f"Error creando orden desde CSV: {e}")
        return jsonify({'message': str(e)}), 500
    
@order_api.route('/order/auto_order/<string:order_number>', methods=['GET'])
def update_order_from_csv(order_number, filename='clinica_daniel.csv'):
    try:
        # Construir ruta al archivo CSV desde el directorio de ejecución
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({'message': f'CSV file not found: {filename}'}), 404

        # Buscar la orden existente
        order = Order.find_by_order_number(order_number=order_number)
        if not order:
            return jsonify({'message': f'Order {order_number} not found'}), 404

        # Leer CSV con separador ;
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')

            updated_products = []
            total = 0.0

            for row in reader:
                sku = row.get('SKU').strip() if row.get('SKU') else ''
                quantity = limpiar_valor(row.get('CANTIDAD'))
                price = limpiar_valor(row.get('PRECIO'))
                print(f"Processing SKU: {sku}, Quantity: {quantity}, Price: {price}")
                if not sku:
                    continue

                product = Product.find_by_sku(sku=sku)
                if not product:
                    continue

                product_dict = product
                product_dict['quantity'] = quantity
                product_dict['price_sale'] = price
                updated_products.append(product_dict)
                total += quantity * price
        order.products = updated_products
        order.updated()

        return jsonify({'message': 'Order updated successfully'}), 200

    except Exception as e:
        print(f"Error updating order from CSV: {e}")
        return jsonify({'message': str(e)}), 500