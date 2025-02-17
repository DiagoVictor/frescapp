from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
cierres_collection = db['cierres']

class Cierre:
    def __init__(self, id=None, fecha=None, efectivo=None, davivienda=None, bancolombia=None, cartera=None, inventario_hoy=None, inventario_ayer=None, ruta=None, aux_ops=None, cogs=None, cash_margin=None, efectivo_total=None, davivienda_total=None, bancolombia_total=None, cartera_total=None, cierre_total=None,deuda_total=None):
        self.id = id
        self.fecha = fecha
        self.efectivo = efectivo
        self.davivienda = davivienda
        self.bancolombia = bancolombia
        self.cartera = cartera
        self.inventario_hoy = inventario_hoy
        self.inventario_ayer = inventario_ayer
        self.ruta = ruta
        self.aux_ops = aux_ops
        self.cogs = cogs
        self.cash_margin = cash_margin
        self.efectivo_total = efectivo_total
        self.davivienda_total = davivienda_total
        self.bancolombia_total = bancolombia_total
        self.cartera_total = cartera_total
        self.cierre_total = cierre_total
        self.deuda_total = deuda_total

    def crear(self):
        cierre_data = {
            "fecha": self.fecha if self.fecha else datetime.now(),
            "efectivo": self.efectivo,
            "davivienda": self.davivienda,
            "bancolombia": self.bancolombia,
            "cartera": self.cartera,
            "inventario_hoy": self.inventario_hoy,
            "inventario_ayer": self.inventario_ayer,
            "ruta": self.ruta,
            "aux_ops": self.aux_ops,
            "cogs": self.cogs,
            "cash_margin": self.cash_margin,
            "efectivo_total": self.efectivo_total,
            "davivienda_total": self.davivienda_total,
            "bancolombia_total": self.bancolombia_total,
            "cartera_total": self.cartera_total,
            "cierre_total": self.cierre_total,
            "deuda_total" : self.deuda_total
        }
        result = cierres_collection.insert_one(cierre_data)
        self.id = result.inserted_id
        return self.id

    def editar(self):
        if not self.id:
            raise ValueError("Se requiere un ID para editar el cierre.")
        cierre_data = {
            "fecha": self.fecha,
            "efectivo": self.efectivo,
            "davivienda": self.davivienda,
            "bancolombia": self.bancolombia,
            "cartera": self.cartera,
            "inventario_hoy": self.inventario_hoy,
            "inventario_ayer": self.inventario_ayer,
            "ruta": self.ruta,
            "aux_ops": self.aux_ops,
            "cogs": self.cogs,
            "cash_margin": self.cash_margin,
            "efectivo_total": self.efectivo_total,
            "davivienda_total": self.davivienda_total,
            "bancolombia_total": self.bancolombia_total,
            "cartera_total": self.cartera_total,
            "cierre_total": self.cierre_total,
            "deuda_total" : self.deuda_total
        }
        cierres_collection.update_one({"_id": ObjectId(self.id)}, {"$set": cierre_data})

    def eliminar(self):
        if not self.id:
            raise ValueError("Se requiere un ID para eliminar el cierre.")
        cierres_collection.delete_one({"_id": ObjectId(self.id)})

    @staticmethod
    def listar():
        return list(cierres_collection.find())

    @staticmethod
    def obtener_por_id(id):
        return cierres_collection.find_one({"_id": ObjectId(id)})