from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
orders_collection = db['orders']  

class Order:
    def __init__(self, 
                 order_number,
                 customer_email, 
                 customer_phone,
                 customer_documentNumber,
                 customer_documentType,
                 customer_name,
                 delivery_date, 
                 status, 
                 created_at, 
                 updated_at, 
                 products,
                 total,
                 deliverySlot,
                 paymentMethod,
                 deliveryAddress,
                 deliveryAddressDetails,
                 discount=None 
                 ):
        self.order_number = order_number
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_documentNumber = customer_documentNumber
        self.customer_documentType = customer_documentType
        self.customer_name = customer_name
        self.delivery_date = delivery_date
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.products = products
        self.total = total
        self.deliverySlot = deliverySlot
        self.paymentMethod = paymentMethod
        self.deliveryAddress = deliveryAddress
        self.deliveryAddressDetails = deliveryAddressDetails 
        self.discount = discount if discount is not None else 0  

    def save(self):
        order_data = {
            "order_number" : self.order_number,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "customer_documentNumber": self.customer_documentNumber,
            "customer_documentType": self.customer_documentType,
            "customer_name": self.customer_name,
            "delivery_date": self.delivery_date,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at" : self.updated_at,
            "products" : self.products,
            "total" : self.total,
            "deliverySlot" : self.deliverySlot,
            "paymentMethod" : self.paymentMethod,
            "deliveryAddress" : self.deliveryAddress,
            "deliveryAddressDetails" : self.deliveryAddressDetails,
            "discount" : self.discount 
        }
        result = orders_collection.insert_one(order_data)
        return result.inserted_id
    
    def updated(self):
        orders_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "order_number" :self.order_number,
                        "customer_email": self.customer_email,
                        "customer_phone": self.customer_phone,
                        "customer_documentNumber": self.customer_documentNumber,
                        "customer_documentType": self.customer_documentType,
                        "customer_name": self.customer_name,
                        "delivery_date": self.delivery_date,
                        "status": self.status,
                        "created_at": self.created_at,
                        "updated_at" : self.updated_at,
                        "products" : self.products,
                        "total" : self.total,
                        "deliverySlot" : self.deliverySlot,
                        "paymentMethod" : self.paymentMethod,
                        "deliveryAddress" : self.deliveryAddress,
                        "deliveryAddressDetails" : self.deliveryAddressDetails 
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
    @staticmethod
    def find_by_customer(customer_email):
        return orders_collection.find({"customer_email": customer_email})