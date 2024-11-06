from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
routes_collection = db['routes']

class Route:
    def __init__(self, route_number, close_date, driver, stops=None, cost=0, id=None):
        self.id = id  # Aquí `id` es opcional
        self.route_number = route_number
        self.close_date = close_date
        self.driver = driver
        self.stops = stops if stops is not None else []
        self.cost = cost

    def save(self):
        route_data = {
            "route_number": self.route_number,
            "close_date": self.close_date,
            "driver": self.driver,
            "stops": self.stops,
            "cost": self.cost
        }
        result = routes_collection.insert_one(route_data)
        self.id = str(result.inserted_id)
        return self.id

    def update(self):
        routes_collection.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "route_number": self.route_number,
                "close_date": self.close_date,
                "driver": self.driver,
                "stops": self.stops,
                "cost": self.cost
            }}
        )

    @staticmethod
    def objects():
        return routes_collection.find().sort("close_date", -1)

    @staticmethod
    def object(id):
        route_data = routes_collection.find_one({'_id': ObjectId(id)})
        if route_data:
            route_data['id'] = str(route_data['_id'])
            return route_data
        return None

    @staticmethod
    def find_by_route_number(route_number):
        route = routes_collection.find_one({"route_number": int(route_number)})
        if route:
            route['id'] = str(route['_id'])
        return route
    
    def delete_route(self):
        result = routes_collection.delete_one({"_id": ObjectId(self.id)})
        if result.deleted_count > 0:
            print("Route deleted successfully.")
        else:
            print("Route not found.")
