from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://3.23.102.32:27017/') 
db = client['frescapp'] 
customers_collection = db['customer']  

class Customer:
    def __init__(self, 
                 phone, 
                 name, 
                 address, 
                 email, 
                 status, 
                 created_at, 
                 updated_at, 
                 password,
                 category):
        self.phone = phone
        self.name = name
        self.address = address
        self.email = email
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.password = password
        self.category = category

    def save(self):
        customer_data = {
            "phone": self.phone,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at" : self.updated_at,
            "password" : self.password,
            "category" : self.category
        }
        result = customers_collection.insert_one(customer_data)
        return result.inserted_id
    
    def updated(self):
        customers_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "phone": self.phone,
                        "name": self.name,
                        "address": self.address,
                        "email": self.email,
                        "status": self.status,
                        "created_at": self.created_at,
                        "updated_at" : self.updated_at,
                        "password" : self.password,
                        "category" : self.category
                    }
            }
        )
    

    @staticmethod
    def objects():
        return customers_collection.find()
    @staticmethod
    def object(id):
        customer_data = customers_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if customer_data:
            return Customer(**customer_data)
        else:
            return None
    @staticmethod
    def find_by_email(email):
        return customers_collection.find_one({"email": email})
