from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
products_collection = db['products']  
customers_collection = db['customers']  

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
                 status,
                 root,
                 child,
                 step_unit,
                 step_unit_sipsa,
                 factor_volumen,
                 sipsa_id,
                 proveedor,
                 rate_root,
                 last_price_purchase,
                 quantity):
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
        self.root = root
        self.child = child
        self.step_unit = step_unit
        self.proveedor = proveedor
        self.rate_root = rate_root
        self.step_unit_sipsa = step_unit_sipsa
        self.factor_volumen = factor_volumen
        self.sipsa_id = sipsa_id
        self.last_price_purchase = last_price_purchase
        self.quantity = quantity

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
            "status" : self.status,
            "step_unit_sipsa" : self.step_unit_sipsa,
            "factor_volumen" : self.factor_volumen,
            "sipsa_id" : self.sipsa_id,
            "last_price_purchase" : self.last_price_purchase,
            "quantity" : int(self.quantity),
            "root":self.root,
            "child": self.child,
            "step_unit":self.step_unit,
            "proveedor" : self.proveedor,
            "rate_root" : self.rate_root
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
                        "status" : self.status,
                        "step_unit_sipsa" : self.step_unit_sipsa,
                        "factor_volumen" : self.factor_volumen,
                        "sipsa_id" : self.sipsa_id,
                        "last_price_purchase" : self.last_price_purchase,
                        "quantity" : self.quantity,
                        "root":self.root,
                        "child": self.child,
                        "step_unit":self.step_unit,
                        "proveedor" : self.proveedor,
                        "rate_root" : self.rate_root
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
    def objects_customer(status, customer_email):
        if customer_email == 'undefined':
            customer_product_skus = []
        else:
            customer = customers_collection.find_one({"email": customer_email})
            customer_product_skus = customer.get('list_products', [])
        
        all_active_products = list(products_collection.find({"status": status}))
        
        product_dict = {product['sku']: product for product in all_active_products}
        
        ordered_products = []
        for product_sku in customer_product_skus:
            if product_sku in product_dict:
                ordered_products.append(product_dict.pop(product_sku))
        
        remaining_products = list(product_dict.values())
        ordered_products.extend(remaining_products)
        
        return ordered_products

    @staticmethod
    def object(id):
        product_data = products_collection.find_one({'_id': ObjectId(id) }, {'_id': 0})
        if product_data:
            return Product(**product_data)
        else:
            return None
    @staticmethod
    def find_by_sku(sku):
        return products_collection.find_one({"sku": sku},  {'_id': 0})