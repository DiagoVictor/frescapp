from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
purchase_collection = db['purchases']  
class Purchase:
    def __init__(self, 
                 date=None, 
                 purchase_number=None, 
                 status=None,
                 products = None,
                 _id=None):
        self.date = date
        self.purchase_number = purchase_number
        self.status = status
        self.products = products if products is not None else [] 
        self.id = _id
    @staticmethod
    def total_by_date(fecha):
        try:
            purchase = purchase_collection.find_one({"date": fecha})
            
            if not purchase:
                return 0  # Si no hay inventario para esa fecha, retornar 0
            
            products = purchase.get("products", [])
        
            total = sum((product.get("final_price_purchase") or 0) * (product.get("total_quantity") or 0) for product in products)
            
            return total
        except Exception as e:
            print(f"Error al calcular el total para la fecha {fecha}: {e}")
            return 0
    @staticmethod
    def get_by_date(fecha):
        purchase = purchase_collection.find_one({"date": fecha})
        if purchase:
            return Purchase(
                date=purchase.get("date"),
                purchase_number=purchase.get("purchase_number"),
                status=purchase.get("status"),
                products=purchase.get("products"),
                _id=str(purchase["_id"])
            )
        return None