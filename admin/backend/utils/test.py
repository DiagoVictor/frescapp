from pymongo import MongoClient

# Conexión a la base de datos
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp') 
db = client['frescapp']
customers_collection = db['customers']  

try:
    # Iterar sobre todos los documentos de la colección
    for doc in customers_collection.find({}, {"_id": 1, "email": 1}):  # Recuperamos _id y email
        email = doc.get("email")  # Obtener el valor del campo email
        if email:  # Asegurarnos de que el campo email exista y no sea None
            # Actualizar el documento con el nuevo campo user
            customers_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"user": email}}
            )
    print("Todos los documentos han sido actualizados correctamente.")

except Exception as e:
    print(f"Error al actualizar documentos: {e}")

finally:
    # Cerrar la conexión
    client.close()