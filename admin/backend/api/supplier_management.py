from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import certifi

supplier_api = Blueprint('supplier', __name__)
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
supplier_collection = db['suppliers']

# Ruta para listar todos los proveedores
@supplier_api.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = list(supplier_collection.find({}, {'_id': 0}).sort('name', 1))
    return jsonify(suppliers), 200

# Ruta para crear un nuevo proveedor
@supplier_api.route('/supplier', methods=['POST'])
def create_supplier():
    data = request.json
    if not all(k in data for k in ('name', 'nit', 'email', 'address')):
        return jsonify({"status": "failure", "message": "Missing fields in request."}), 400
    
    supplier = {
        "name": data['name'],
        "nit": data['nit'],
        "email": data['email'],
        "address": data['address']
    }
    
    supplier_collection.insert_one(supplier)
    return jsonify({"status": "success", "message": "Supplier created successfully."}), 201

# Ruta para editar un proveedor existente
@supplier_api.route('/supplier/<string:nit>', methods=['PUT'])
def edit_supplier(nit):
    data = request.json
    result = supplier_collection.update_one(
        {"nit": nit},
        {"$set": data}
    )
    if result.matched_count:
        return jsonify({"status": "success", "message": "Supplier updated successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404

# Ruta para eliminar un proveedor
@supplier_api.route('/supplier/<string:nit>', methods=['DELETE'])
def delete_supplier(nit):
    result = supplier_collection.delete_one({"nit": nit})
    if result.deleted_count:
        return jsonify({"status": "success", "message": "Supplier deleted successfully."}), 200
    else:
        return jsonify({"status": "failure", "message": "Supplier not found."}), 404
