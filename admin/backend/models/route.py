from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
routes_collection = db['routes']  # Colección de rutas

class Route:
    def __init__(self, route_number, close_date, driver, stops=None):
        self.route_number = route_number
        self.close_date = close_date
        self.driver = driver
        self.stops = stops if stops is not None else []  # Iniciar como lista vacía si no se proporcionan paradas

    def save(self):
        route_data = {
            "route_number": self.route_number,
            "close_date": self.close_date,
            "driver": self.driver,
            "stops": self.stops  # Guardar el atributo stops
        }
        result = routes_collection.insert_one(route_data)
        return result.inserted_id

    def update(self):
        routes_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "route_number": self.route_number,
                "close_date": self.close_date,
                "driver": self.driver,
                "stops": self.stops  # Actualizar el atributo stops
            }}
        )

    @staticmethod
    def objects():
        return routes_collection.find()

    @staticmethod
    def object(id):
        route_data = routes_collection.find_one({'_id': ObjectId(id)}, {'_id': 0})
        if route_data:
            return Route(**route_data)
        else:
            return None

    @staticmethod
    def find_by_route_number(route_number):
        return routes_collection.find_one({"route_number": route_number}, {'_id': 0})
