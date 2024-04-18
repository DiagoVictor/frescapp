from flask import Blueprint, jsonify, request
import json
from datetime import datetime
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('mongodb://3.23.102.32:27017/') 
db = client['frescapp'] 
config_collection = db['orderConfig']  

configOrder_api = Blueprint('config_order', __name__)

@configOrder_api.route('/configOrder', methods=['GET'])
def configOrder():
    data = config_collection.find()
    data_json = dumps(data)
    return data_json, 200
