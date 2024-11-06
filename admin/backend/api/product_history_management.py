from flask import Blueprint, jsonify, request
from models.product_history import ProductHistory
import json, dump
from flask_bcrypt import Bcrypt
from datetime import datetime
from decimal import Decimal
import pandas as pd
import os
import json
from pymongo import MongoClient
product_history_api = Blueprint('products_history', __name__)

@product_history_api.route('/products_history/<string:operation_date_start>/<string:operation_date_end>', methods=['GET'])
def list_products_history(operation_date_start,operation_date_end):
    products_cursor = ProductHistory.objects(operation_date_start,operation_date_end)

    product_data = [
        {
            "id": str(product["_id"]), 
            "operation_date": product["operation_date"],
            "name": product["name"],
            "unit": product["unit"],
            "category": product["category"],
            "sku": product["sku"],
            "root": product["root"],
            "child" : product["child"],
            "step_unit" : product["step_unit"],
            "margen" : product["margen"],
            "last_price_purchased" : product["last_price_purchased"],
            "minimoKg" : product["minimoKg"],
            "maximoKg" : product["maximoKg"],
            "promedioKg" : product["promedioKg"],
            "price_sale" : product["price_sale"],
            "price_purchase" : product["price_purchase"],
            "last_price_purchase" : product["last_price_purchase"],
            "last_price_sale" : product["last_price_sale"],
            "factor_volumen" : product["factor_volumen"],
            "sipsa_id" : product["sipsa_id"]
        }
        for product in products_cursor
    ]
    products_json = json.dumps(product_data)
    return products_json, 200