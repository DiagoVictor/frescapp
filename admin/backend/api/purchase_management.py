from flask import Blueprint, jsonify, request
from pymongo import MongoClient

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
