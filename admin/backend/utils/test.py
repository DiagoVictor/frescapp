from pymongo import MongoClient

# Conexión a la base de datos MongoDB
client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = client['frescapp']
collection = db['orders']

# Actualizar el estado de todas las órdenes a "Facturada"
try:
    # Realiza la actualización de los documentos
    result = collection.update_many(
        {},  # Filtro vacío para afectar a todos los documentos
        {'$set': {'status': 'Facturada'}}  # Establece el estado a "Facturada"
    )
    
    # Imprime el número de documentos actualizados
    print(f'Número de órdenes actualizadas: {result.modified_count}')

except Exception as e:
    # Manejo de errores
    print(f'Ocurrió un error al actualizar las órdenes: {e}')

finally:
    # Cerrar la conexión
    client.close()
