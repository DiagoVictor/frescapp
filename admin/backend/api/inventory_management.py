from models.inventory import Inventory
from models.product import Product
from flask import Blueprint, jsonify, request

inventory_api = Blueprint('inventory', __name__)


@inventory_api.route('/inventories', methods=['GET'])
def get_inventories():
    items = Inventory.get_all()
    return jsonify([{
        "id": str(item["_id"]),
        "close_date": item.get("close_date"),
        "products": item.get("products", [])
    } for item in items])

@inventory_api.route('/inventory/<inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    item = Inventory.get_by_id(inventory_id)
    if not item:
        return jsonify({"message": "Inventory not found"}), 404

    # Construir la respuesta con los datos del inventario
    response = {
        "id": str(item.id),
        "close_date": item.close_date,
        "products": [
            {
                "sku": product.get("sku"),
                "name": product.get("name"),
                "category": product.get("category"),
                "quantity": product.get("quantity", 0),
                "cost": product.get("cost", 0)
            }
            for product in item.products
        ]
    }
    return jsonify(response), 200

@inventory_api.route('/create/<close_date>', methods=['POST'])
def create_inventory(close_date):
    data = request.json
    products_data = Product.objects("active")
    filtered_products = [
        {
            "sku": product["sku"],
            "name": product["name"],
            "category": product["category"],
            "quantity": 0,  
            "cost": product["price_purchase"]
        }
        for product in products_data
    ]
    item = Inventory(
        close_date=close_date,
        products=filtered_products
    )
    item.save()
    return jsonify({"message": "Inventory item added successfully", "id": item.id}), 201

@inventory_api.route('/inventory/<inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    data = request.json
    item = Inventory.get_by_id(inventory_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    item.close_date = data.get('close_date', item.close_date)
    item.products = data.get('products', item.products)
    item.save()
    return jsonify({"message": "Inventory updated successfully"})

@inventory_api.route('/inventory/<inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    deleted_count = Inventory.delete_by_id(inventory_id)
    if deleted_count:
        return jsonify({"message": "Inventory deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

