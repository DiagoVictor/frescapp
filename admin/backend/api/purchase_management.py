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
from pymongo import MongoClient
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak
import locale
import certifi
import urllib.request


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
                "proveedor": "",
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
    purchases = list(purchase_collection.find({}, {'_id': 0}).sort('date', -1))
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

@purchase_api.route('/purchase/<string:purchase_number>', methods=['DELETE'])
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
    status = data.get("status")
    if purchase:
        updated = False
        for product in purchase['products']:
            if product['sku'] == sku:
                # Actualiza el precio del producto
                product['final_price_purchase'] = new_price
                product['proveedor'] = new_proveedor
                product['status'] = status
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


@purchase_api.route('/purchase/report/<string:purchase_number>', methods=['GET'])
def get_report_purchase(purchase_number):
    pipeline = [
        {
            "$match": {
                "purchase_number": str(purchase_number)  # Asegúrate de que `purchase_number` es una cadena
            }
        },
        {
            "$unwind": "$products"
        },
        {
            "$unwind": "$products.clients"
        },
        {
            "$group": {
                "_id": {
                    "sku": "$products.sku",
                    "name": "$products.name",
                    "price_purchase": "$products.price_purchase",
                    "proveedor": "$products.proveedor.name",
                    "category": "$products.category",
                    "unit": "$products.unit"
                },
                "total_quantity_ordered": {"$sum": "$products.clients.quantity"},
                "clients_quantities": {"$push": {"client_name": "$products.clients.client_name", "quantity": "$products.clients.quantity"}},
                "date": {"$first": "$date"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "sku": "$_id.sku",
                "name": "$_id.name",
                "total_quantity_ordered": 1,
                "price_purchase": "$_id.price_purchase",
                "proveedor": "$_id.proveedor",
                "category": "$_id.category",
                "unit": "$_id.unit",
                "date": 1,
                "clients_quantities": {
                    "$reduce": {
                        "input": "$clients_quantities",
                        "initialValue": "",
                        "in": {
                            "$concat": [
                                "$$value",
                                {
                                    "$cond": {
                                        "if": {"$eq": ["$$value", ""]},
                                        "then": "",
                                        "else": " - "
                                    }
                                },
                                {"$concat": [ {"$toString": "$$this.quantity"}]}
                            ]
                        }
                    }
                }
            }
        },
        {
            "$sort": {
                "category": 1,
                "name": 1
            }
        }
    ]

    products = list(purchase_collection.aggregate(pipeline))

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    image_url = 'https://buyfrescapp.com/images/banner1.png'
    context = urllib.request.ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(image_url, context=context) as response:
        image_data = response.read()
    image_stream = BytesIO(image_data)
    logo = Image(image_stream, width=200, height=70)
    centered_style = ParagraphStyle(
        name='Centered',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.white,
        leading=50
    )

    pdf_content = []
    header_paragraph = Paragraph(
        '<font>Compras para el {}</font>'.format(str(products[0].get('date'))),
        centered_style
    )
    green_box = Table([[header_paragraph]], colWidths=[250], rowHeights=[70], style=[('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#97D700'))])
    content_table = Table([
        [logo, green_box]], colWidths=[200, 250])
    pdf_content.append(content_table)
    pdf_content.append(Paragraph('<br/><br/>', styles['Normal']))
    
    table_width = 500
    product_data = [
        ['Nombre', 'Categoria', 'Cant. Total',  'Pick','Precio Unit.', 'Precio Real', 'Proveedor'],  # Encabezado
    ]

    word_wrap_style = styles["Normal"]
    word_wrap_style.wordWrap = 'CJK'

    for product in products:
        name = product['name'] + " - ( " + product['sku'] + " )"
        clients_quantities = Paragraph(product['clients_quantities'], word_wrap_style)
        quantity = Paragraph(str(product.get('total_quantity_ordered')) + "  " + str(product.get('unit')), word_wrap_style)
        price = locale.format_string('%.2f', round(product.get('price_purchase'),0), grouping=True)
        proveedor =  Paragraph('',word_wrap_style)
        name_paragraph = Paragraph(name, word_wrap_style)
        product_row = [name_paragraph, product.get('category'), quantity, clients_quantities, price, '', proveedor]
        product_data.append(product_row)
    
    total = locale.format_string('%.2f',sum(round(float(product['total_quantity_ordered']) * float(product['price_purchase']),0) for product in products), grouping=True)
    product_data.extend([['', '', '', '', '', ''],
                         ['', '', '', 'Total', total, '']])
    
    col_widths = [(2 / 8) * table_width] + [(1 / 8) * table_width] * 5
    product_table = Table(product_data, colWidths=col_widths)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97D700')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    
    pdf_content.append(product_table)
    pdf_content.append(PageBreak())

    pdf.build(pdf_content)
    buffer.seek(0)
    response = Response(buffer, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=compra_num_{}_{}.pdf'.format(purchase_number, purchase_number)
    return response
