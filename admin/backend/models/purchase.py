from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
orders_collection = db['purchases']  

class Purchase:
    def __init__(self
                 ,order_number
                 ,close_date
                 ,supplier
    )