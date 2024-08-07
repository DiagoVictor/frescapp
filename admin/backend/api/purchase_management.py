from flask import Blueprint, jsonify, request
from pymongo import MongoClient
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
purchase_api = Blueprint('purchase', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
orders_collection = db['orders']
purchase_collection = db['purchases']

@purchase_api.route('/create/<string:date>', methods=['GET'])
def create_purchase(date):
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
                "_id": {
                    "sku": "$products.sku",
                    "client_name": "$customer_name"  # Asume que hay un campo client_name en la orden
                },
                "total_quantity_ordered": {"$sum": "$products.quantity"}
            }
        },
        {
            "$group": {
                "_id": "$_id.sku",
                "total_quantity_ordered": {"$sum": "$total_quantity_ordered"},
                "clients": {
                    "$push": {
                        "client_name": "$_id.client_name",
                        "quantity": "$total_quantity_ordered"
                    }
                }
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
                "category": "$product_info.category",
                "unit": "$product_info.unit",
                "status": "Creada",
                "link_document_support": "",
                "final_price_purchase": {"$literal": 0.0},
                "clients": 1
            }
        }
    ]

    products = list(orders_collection.aggregate(pipeline))
    if products:
        purchase_number = db['counters'].find_one_and_update(
            {"_id": "purchase_id"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=True
        )["sequence_value"]
        purchase_document = {
            "date": date,
            "purchase_number": str(purchase_number),
            "status": "Creada",
            "products": products
        }
        purchase_collection.insert_one(purchase_document)
        return jsonify({"status": "success", "message": "Purchase document saved.", "purchase_number": purchase_number}), 201
    else:
        return jsonify({"status": "failure", "message": "No products found for the given date."}), 404

@purchase_api.route('/purchases', methods=['GET'])
def list_purchases():
    purchases = list(purchase_collection.find({}, {'_id': 0}))
    return jsonify(purchases), 200

@purchase_api.route('/purchase/<string:purchaseNumber>', methods=['GET'])
def get_purchase(purchaseNumber):
    purchase = purchase_collection.find_one({"purchase_number" : purchaseNumber}, {'_id': 0})
    return jsonify(purchase), 200

@purchase_api.route('/purchase/<int:purchase_number>', methods=['PUT'])
def edit_purchase(purchase_number):
    data = request.json
    result = purchase_collection.update_one(
        {"purchase_number": purchase_number},
        {"$set": data}
    )
    if result.matched_count:
        return jsonify({"status": "success", "message": "Purchase updated successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

@purchase_api.route('/purchase/<int:purchase_number>', methods=['DELETE'])
def delete_purchase(purchase_number):
    result = purchase_collection.delete_one({"purchase_number": purchase_number})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Purchase deleted successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404

@purchase_api.route('/update_price', methods=['POST'])
def update_price():
    data = request.json
    purchase_number = data.get("purchase_number")
    sku = data.get("sku")
    new_price = data.get("final_price_purchase")
    new_proveedor = data.get("proveedor")
    purchase = purchase_collection.find_one({"purchase_number": purchase_number})

    if purchase:
        updated = False
        for product in purchase['products']:
            if product['sku'] == sku:
                # Actualiza el precio del producto
                product['final_price_purchase'] = new_price
                product['proveedor'] = new_proveedor
                updated = True
                break

        if updated:
            purchase_collection.update_one(
                {"purchase_number": purchase_number},
                {"$set": {"products": purchase['products']}}
            )
            return jsonify({"status": "success", "message": "Price updated successfully."}), 200
        else:
            return jsonify({"status": "failure", "message": "SKU not found."}), 404
    else:
        return jsonify({"status": "failure", "message": "Purchase not found."}), 404


@purchase_api.route('/purchase/report/<int:purchase_number>', methods=['GET'])
def get_compras(purchase_number):
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
                "category": "$product_info.category",
                "unit": "$product_info.unit"
            }
        }
    ]
    pipeline.append({
        "$sort": {
            "category": 1 ,
            "name":1
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
    compras_paragraph = Paragraph('<font>Compras para el {}</font>'.format(''), centered_style)
    green_box = Table([[compras_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#97D700'))])
    content_table = Table([
    [logo, green_box]], colWidths=[200, 250])
    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    table_width = 500
    product_data = [
        [ 'Nombre', 'Categoria', 'Cantidad', 'Precio Unitario', 'Proveedor','Proveedor Final', 'Precio Final'],  # Encabezado
    ]
    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    for product in products:
        sku = product['sku']
        name = product['name'] + " - ( "+sku+" )"
        quantity = Paragraph(str(product.get('total_quantity_ordered')) + "  " + str(product.get('unit')),word_wrap_style)
        price = locale.format_string('%.2f', round(product.get('price_purchase'),0), grouping=True)
        proveedor = product['proveedor']
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [ name_paragraph, product.get('category'), quantity, price, proveedor]
        product_data.append(product_row)
    total = locale.format_string('%.2f',sum(round(float(product['total_quantity_ordered']) * float(product['price_purchase']),0) for product in products), grouping=True)
    product_data.extend([['','','','',''],
            ['', '', 'Total', total, '']
        ])
    col_widths = [(2 / 8) * table_width] + [(1 / 8) * table_width] * 4
    product_table = Table(product_data, colWidths=col_widths)
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
    response.headers['Content-Disposition'] = 'inline; filename=ordenes_{}.pdf'.format('')
    return response