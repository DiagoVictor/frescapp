from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://3.23.102.32:27017/') 
db = client['frescapp'] 
orders_collection = db['order']  

class Order:
    def __init__(self, 
                 order_number,
                 customer_email, 
                 delivery_date, 
                 status, 
                 created_at, 
                 updated_at, 
                 products
                 ):
        self.order_number = order_number
        self.customer_email = customer_email
        self.delivery_date = delivery_date
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.products = products

    def save(self):
        order_data = {
            "order_number" : self.order_number,
            "customer_email": self.customer_email,
            "delivery_date": self.delivery_date,
            "status": self.status,
            "created_at": self.created_at,
            "created_at": self.created_at,
            "updated_at" : self.updated_at,
            "products" : self.products
        }
        result = orders_collection.insert_one(order_data)
        return result.inserted_id
    
    def updated(self):
        orders_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "order_number" :self.order_number,
                        "customer_email": self.customer_email,
                        "delivery_date": self.delivery_date,
                        "status": self.status,
                        "status": self.status,
                        "created_at": self.created_at,
                        "updated_at" : self.updated_at,
                        "products" : self.products
                    }
            }
        )
    

    @staticmethod
    def objects():
        return orders_collection.find()
    @staticmethod
    def object(id):
        order_data = orders_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if order_data:
            return Order(**order_data)
        else:
            return None
    @staticmethod
    def find_by_order_number(order_number):
        return orders_collection.find_one({"order_number": order_number})
