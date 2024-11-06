from pymongo import MongoClient
from datetime import datetime
import pandas as pd

def extractDataFromExcel(filepath: str, filter_date: str) -> object:
    # Lee el archivo Excel
    data = pd.read_excel(filepath)

    # Asegúrate de que la columna de fecha esté en formato datetime para compararla
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')

    # Convierte el parámetro filter_date a un objeto datetime
    filter_date = datetime.strptime(filter_date, '%Y-%m-%d')

    # Filtra los registros que coincidan con la fecha especificada
    filtered_data = data[data['FECHA'] == filter_date]

    # Estructura los datos filtrados en una lista de diccionarios
    records = filtered_data.to_dict(orient='records')
    return records

# Copia productos activos y actualiza precios de compra
def copiar_productos_activos_y_actualizar(uri: str, db_name: str, coleccion_origen: str, coleccion_destino: str, operation_date: str, equivalence_data: list):
    client = MongoClient(uri)
    db = client[db_name]

    # Campos a excluir en la consulta
    exclusion = {"_id": 0, "image": 0, "description": 0}
    productos_activos = db[coleccion_origen].find({"status": "active"}, exclusion)
    
    for producto in productos_activos:
        # Obtiene el SKU del producto
        sku = producto.get("sku")
        sku_child = producto.get("child")
        # Busca el precio de compra del día en la colección "purchases" por SKU o por child
        compras = db["purchases"].find_one(
            {
                "date": operation_date,
                "$or": [
                    {"products.sku": sku},
                    {"products.sku": sku_child}
                ]
            },
            {"products.$": 1}
        )


        # Define el precio de compra del día (0 si no se encuentra)
        precio_compra_dia = 0
        if compras and "products" in compras:
            producto_encontrado = compras["products"][0]
            precio_compra_dia = producto_encontrado.get("final_price_purchase", 0)

        # Encuentra la equivalencia
        equivalence_match = next(
            (
                item for item in equivalence_data
                if str(item.get('ARTICULO')) == str(producto.get("sipsa_id")) 
                and pd.to_datetime(item.get('FECHA'), errors='coerce') == pd.to_datetime(operation_date)
            ),
            None
        )
        # Calcula valores mínimos, máximos y promedio
        minimoKg = float(equivalence_match["MINIMO"])  if equivalence_match else 0
        maximoKg = float(equivalence_match["MAXIMO"])  if equivalence_match else 0
        promedioKg = float(equivalence_match["PROMEDIO"])  if equivalence_match else 0

        # Define el price_purchase según la regla dada
        price_purchase = precio_compra_dia if precio_compra_dia != 0 else promedioKg
        if price_purchase == 0:
            price_purchase = producto.get("price_purchase", 0)
        else: 
            price_purchase = price_purchase * float(producto["step_unit"])
            price_purchase = price_purchase * float(producto.get("factor_volumen", 1))

        # Obtiene el margen del producto, asegurando que tenga un valor numérico (ej. 0 si no está presente)
        margen = producto.get("margen", 0)
        minimoKg = minimoKg * float(producto["step_unit"]) 
        maximoKg = maximoKg * float(producto["step_unit"]) 
        promedioKg = promedioKg * float(producto["step_unit"]) 
        # Calcula el price_sale basado en el price_purchase y el margen
        price_sale = price_purchase * (1 + margen)

        # Actualiza el producto con la información nueva
        producto.update({
            "operation_date": operation_date,
            "last_price_purchased": round(precio_compra_dia) if precio_compra_dia else 0,
            "minimoKg": round(minimoKg),
            "maximoKg": round(maximoKg),
            "promedioKg": round(promedioKg),
            "price_purchase": round(price_purchase),
            "price_sale": round(price_sale),
            "last_price_purchase": round(producto.get("price_purchase", 0)),
            "last_price_sale": round(producto.get("price_sale", 0))
        })


        # Inserta el producto actualizado en la colección de destino
        db[coleccion_destino].insert_one(producto)

    client.close()
    print("Productos actualizados y copiados exitosamente.")
def actualizar_precios_en_products(uri: str, db_name: str, coleccion_origen: str, operation_date: str):
    client = MongoClient(uri)
    db = client[db_name]

    # Obtiene los productos de products_history según la operation_date
    productos_history = db[coleccion_origen].find({"operation_date": operation_date})
    
    for producto_hist in productos_history:
        # Busca el producto en products por sku
        sku = producto_hist.get("sku")
        if not sku:
            continue  # Si no tiene SKU, pasa al siguiente producto

        # Actualiza los campos price_sale y price_purchase en products
        db["products"].update_one(
            {"sku": sku},
            {"$set": {
                "price_purchase": producto_hist.get("price_purchase"),
                "price_sale": producto_hist.get("price_sale")
            }}
        )

    client.close()
    print("Precios actualizados en la colección 'products'.")
# Parámetros de conexión y configuración
uri = 'mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp'
db_name = "frescapp"
coleccion_origen = "products"
coleccion_destino = "products_history"
filepath = 'sipsaexporta.xls'  # Cambia esto a la ruta de tu archivo Excel
fields = ['ARTICULO', 'PROMEDIO', 'MINIMO', 'MAXIMO', 'FECHA', 'FUENTE']

fechas_octubre = [
'2024-10-29', '2024-10-30', '2024-10-31' , '2024-11-01' , '2024-11-02' , '2024-11-03' , '2024-11-04', '2024-11-05'
]


for operation_date in fechas_octubre:
    # Extraer datos de acuerdo a la fecha específica
    data = extractDataFromExcel(filepath, operation_date)
    
    # Copiar y actualizar productos activos para la fecha de operación
    copiar_productos_activos_y_actualizar(uri, db_name, coleccion_origen, coleccion_destino, operation_date, data)
    actualizar_precios_en_products(uri, db_name, coleccion_destino, operation_date)
    print("Insertados día  :  " + str(operation_date) )

