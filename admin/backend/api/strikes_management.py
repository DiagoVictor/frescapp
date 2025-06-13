# app/api/strikes_management.py

from flask import Blueprint, jsonify, request
from models.strike import Strike

strike_api = Blueprint('strikes', __name__, url_prefix='/strikes')

@strike_api.route('', methods=['GET'])
def list_strikes():
    order_number = request.args.get('order_number')
    if order_number:
        strikes = Strike.find_by_order(order_number)
    else:
        strikes = Strike.all()
    return jsonify(strikes), 200

@strike_api.route('', methods=['POST'])
def create_strike():
    data = request.get_json()
    strike = Strike(
        order_number      = data['order_number'],
        sku               = data.get('sku'),
        strike_type       = data['strike_type'],
        missing_quantity  = data.get('missing_quantity', 0),
        detail            = data.get('detail')
    )
    new_id = strike.save()
    return jsonify({'id': new_id}), 201

@strike_api.route('/<string:id>', methods=['GET'])
def get_strike(id):
    doc = Strike.get(id)
    if not doc:
        return jsonify({'message': 'Strike not found'}), 404
    return jsonify(doc), 200

@strike_api.route('/<string:id>', methods=['PUT'])
def update_strike(id):
    data = request.get_json()
    existing = Strike.get(id)
    if not existing:
        return jsonify({'message': 'Strike not found'}), 404

    strike = Strike(
        order_number      = data.get('order_number', existing['order_number']),
        sku               = data.get('sku', existing.get('sku')),
        strike_type       = data.get('strike_type', existing['strike_type']),
        missing_quantity  = data.get('missing_quantity', existing.get('missing_quantity', 0)),
        detail            = data.get('detail', existing.get('detail')),
        timestamp         = existing.get('timestamp'),
        id                = id
    )
    strike.update()
    return jsonify({'message': 'updated'}), 200

@strike_api.route('/<string:id>', methods=['DELETE'])
def delete_strike(id):
    existing = Strike.get(id)
    if not existing:
        return jsonify({'message': 'Strike not found'}), 404

    strike = Strike(
        order_number      = existing['order_number'],
        sku               = existing.get('sku'),
        strike_type       = existing['strike_type'],
        missing_quantity  = existing.get('missing_quantity', 0),
        detail            = existing.get('detail'),
        timestamp         = existing.get('timestamp'),
        id                = id
    )
    strike.delete()
    return jsonify({'message': 'deleted'}), 200
