from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument
from ..db import get_db

db = get_db()

resolutions_collection = db['invoice_resolutions']

FIELDS = [
    "alegra_template_id",   # id de la numeración en Alegra
    "prefix",               # ej. FVF
    "from_number",          # desde el número
    "to_number",            # hasta el número
    "last_number",          # último número usado
    "resolution_number",    # número de formulario DIAN
    "resolution_date",      # fecha de formalización (YYYY-MM-DD)
    "valid_until",          # fecha de vencimiento (YYYY-MM-DD)
    "document_type",        # invoice
    "active",
]


class InvoiceResolution:

    @staticmethod
    def _serialize(doc):
        if not doc:
            return None
        doc['id'] = str(doc.pop('_id'))
        doc['text'] = InvoiceResolution.legal_text(doc)
        doc['remaining'] = int(doc.get('to_number', 0)) - int(doc.get('last_number') or int(doc.get('from_number', 1)) - 1)
        return doc

    @staticmethod
    def _clean(data):
        clean = {k: data[k] for k in FIELDS if k in data}
        for k in ("from_number", "to_number", "last_number"):
            if k in clean and clean[k] not in (None, ''):
                clean[k] = int(clean[k])
        if "alegra_template_id" in clean:
            clean["alegra_template_id"] = str(clean["alegra_template_id"]).strip()
        if "prefix" in clean:
            clean["prefix"] = str(clean["prefix"]).strip().upper()
        return clean

    @staticmethod
    def legal_text(res):
        return (
            f"Autorización de numeración de facturación N° {res.get('resolution_number', '')} "
            f"de {res.get('resolution_date', '')} Modalidad Factura Electrónica "
            f"Desde N° {res.get('prefix', '')}{res.get('from_number', '')} "
            f"hasta {res.get('prefix', '')}{res.get('to_number', '')} "
            f"con vigencia hasta {res.get('valid_until', '')}"
        )

    @staticmethod
    def get_all():
        return [InvoiceResolution._serialize(r) for r in resolutions_collection.find().sort("resolution_date", -1)]

    @staticmethod
    def get_by_id(resolution_id):
        return InvoiceResolution._serialize(resolutions_collection.find_one({"_id": ObjectId(resolution_id)}))

    @staticmethod
    def get_active(document_type="invoice"):
        return InvoiceResolution._serialize(
            resolutions_collection.find_one({"active": True, "document_type": document_type})
        )

    @staticmethod
    def create(data):
        doc = InvoiceResolution._clean(data)
        doc.setdefault("document_type", "invoice")
        doc.setdefault("last_number", int(doc.get("from_number", 1)) - 1)
        doc["active"] = False
        doc["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result = resolutions_collection.insert_one(doc)
        if data.get("active"):
            InvoiceResolution.activate(str(result.inserted_id))
        return InvoiceResolution.get_by_id(str(result.inserted_id))

    @staticmethod
    def update(resolution_id, data):
        doc = InvoiceResolution._clean(data)
        doc.pop("active", None)
        resolutions_collection.update_one({"_id": ObjectId(resolution_id)}, {"$set": doc})
        if data.get("active"):
            InvoiceResolution.activate(resolution_id)
        return InvoiceResolution.get_by_id(resolution_id)

    @staticmethod
    def activate(resolution_id):
        res = resolutions_collection.find_one({"_id": ObjectId(resolution_id)})
        if not res:
            return None
        resolutions_collection.update_many(
            {"document_type": res.get("document_type", "invoice"), "_id": {"$ne": res["_id"]}},
            {"$set": {"active": False}}
        )
        resolutions_collection.update_one({"_id": res["_id"]}, {"$set": {"active": True}})
        return InvoiceResolution.get_by_id(resolution_id)

    @staticmethod
    def delete(resolution_id):
        return resolutions_collection.delete_one({"_id": ObjectId(resolution_id), "active": {"$ne": True}}).deleted_count

    @staticmethod
    def next_number(resolution_id):
        """Reserva de forma atómica el siguiente consecutivo de la resolución. None si se agotó."""
        res = resolutions_collection.find_one({"_id": ObjectId(resolution_id)})
        if not res:
            return None
        updated = resolutions_collection.find_one_and_update(
            {"_id": res["_id"], "last_number": {"$lt": int(res["to_number"])}},
            {"$inc": {"last_number": 1}},
            return_document=ReturnDocument.AFTER
        )
        return updated["last_number"] if updated else None

    @staticmethod
    def check_usable(res):
        """Devuelve un mensaje de error si la resolución no se puede usar, o None."""
        if not res:
            return "No hay una resolución de facturación activa. Configúrala en el admin (Resoluciones)."
        if not res.get("alegra_template_id"):
            return "La resolución activa no tiene el id de numeración de Alegra."
        today = datetime.now().strftime('%Y-%m-%d')
        if res.get("valid_until") and res["valid_until"] < today:
            return f"La resolución {res.get('prefix')} venció el {res['valid_until']}."
        if res.get("remaining", 1) <= 0:
            return f"La resolución {res.get('prefix')} agotó su rango de numeración."
        return None
