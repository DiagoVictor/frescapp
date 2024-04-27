from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@3.23.102.32:27017/frescapp') 
db = client['frescapp']
products_collection = db['products']  

class Product:
    def __init__(self, 
                 name, 
                 unit, 
                 category, 
                 sku, 
                 price_sale, 
                 price_purchase, 
                 discount, 
                 margen,
                 iva,
                 iva_value,
                 description,
                 image,
                 status):
        self.name = name
        self.unit = unit
        self.category = category
        self.sku = sku
        self.price_sale = price_sale
        self.price_purchase = price_purchase
        self.discount = discount
        self.margen = margen
        self.iva = iva
        self.iva_value = iva_value
        self.description = description
        self.image = image
        self.status = status

    def save(self):
        product_data = {
            "name": self.name,
            "unit": self.unit,
            "category": self.category,
            "sku": self.sku,
            "price_sale": self.price_sale,
            "price_purchase": self.price_purchase,
            "discount" : self.discount,
            "margen" : self.margen,
            "iva" : self.iva,
            "iva_value" : self.iva_value,
            "description" : self.description,
            "image" : self.image,
            "status" : self.status
        }
        result = products_collection.insert_one(product_data)
        return result.inserted_id
    
    def updated(self):
        products_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": { 
                        "name": self.name,
                        "unit": self.unit,
                        "category": self.category,
                        "sku": self.sku,
                        "price_sale": self.price_sale,
                        "price_purchase": self.price_purchase,
                        "discount" : self.discount,
                        "margen" : self.margen,
                        "iva" : self.iva,
                        "iva_value" : self.iva_value,
                        "description" : self.description,
                        "image" : self.image,
                        "status" : self.status
                    }
            }
        )
    

    @staticmethod
    def objects():
        return products_collection.find()
    @staticmethod
    def objects(status):
        return products_collection.find({"status": status})
    @staticmethod
    def object(id):
        product_data = products_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if product_data:
            return Product(**product_data)
        else:
            return None
    @staticmethod
    def find_by_sku(sku):
        return Product(**products_collection.find_one({"sku": sku},  {'_id': 0}))
