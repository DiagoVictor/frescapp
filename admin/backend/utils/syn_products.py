import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import json

# Configurar acceso a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
path_file = 'C:/Users/USUARIO/Documents/frescapp/admin/backend/utils/'
creds = ServiceAccountCredentials.from_json_keyfile_name('ruta/al/archivo/credenciales.json', scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
spreadsheet = client.open("Nombre de la hoja de cálculo")
worksheet = spreadsheet.sheet1  # Acceder a la primera hoja

# Obtener todos los registros
records = worksheet.get_all_records()

# Convertir a DataFrame
df = pd.DataFrame(records)

# Convertir DataFrame a JSON
json_data = df.to_json(orient='records')

# Convertir cadena JSON a objetos de Python
data = json.loads(json_data)

# Configurar la conexión a MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["nombre_de_la_base_de_datos"]
collection = db["nombre_de_la_coleccion"]

# Insertar los datos en MongoDB
collection.insert_many(data)

print("Datos importados a MongoDB exitosamente.")
