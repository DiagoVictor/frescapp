from pymongo import MongoClient
from bson import ObjectId

# Configuración del cliente de MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
inventory_collection = db['inventory']  

class Inventory:
    def __init__(self, 
                 close_date=None, 
                 products=None, 
                 _id=None):
        self.close_date = close_date
        self.products = products if products is not None else []  # Lista de productos
        self.id = _id

    def save(self):
        item_data = {
            "close_date": self.close_date,
            "products": self.products
        }
        if self.id:
            inventory_collection.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": item_data}
            )
        else:
            result = inventory_collection.insert_one(item_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def get_all():
        return list(inventory_collection.find())

    @staticmethod
    def get_by_id(inventory_id):
        item = inventory_collection.find_one({"_id": ObjectId(inventory_id)})
        if item:
            return Inventory(
                close_date=item.get("close_date"),
                products=item.get("products"),
                _id=str(item["_id"])
            )
        return None

    @staticmethod
    def delete_by_id(item_id):
        return inventory_collection.delete_one({"_id": ObjectId(item_id)}).deleted_count
