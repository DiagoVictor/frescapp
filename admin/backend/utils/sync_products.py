import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
import json
from pymongo import MongoClient
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
def authenticate():
    if os.name == 'posix':  # Linux o macOS
        path_file = '/home/ubuntu/frescapp/admin/backend/utils/'
    elif os.name == 'nt':  # Windows
        path_file = 'C:/Users/USUARIO/Documents/frescapp/admin/backend/utils/'
    credential_path = os.path.join(path_file, 'credentials_spread.json')
    if not os.path.exists(credential_path):
        raise FileNotFoundError(f"El archivo de credenciales no se encontró en {credential_path}")
    creds = Credentials.from_service_account_file(credential_path, scopes=scope)
    return creds
credentials = authenticate()
client = gspread.authorize(credentials)
spreadsheet_id = "1efvIDyxsO0n2A4P_lZj1BUNy-SV_5d5zm9m8CMUI9mc"
spreadsheet = client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.sheet1  # Acceder a la primera hoja
records = worksheet.get_all_records()
df = pd.DataFrame(records)
df = df[df['status'] == 'active']
df = df.drop(columns=['pricing'], errors='ignore')
df['iva'] = df['iva'].astype(bool)
df['quantity'] = 0
json_data = df.to_json(orient='records', date_format='iso')
mongo_client = MongoClient('mongodb://admin:Caremonda@app.buyfrescapp.com:27017/frescapp')
db = mongo_client['frescapp']
collection = db['products']
collection.delete_many({})
data = json.loads(json_data)
collection.insert_many(data)
collection.update_many(
    {},
    [
        { '$set': { 'price_sale': { '$toDouble': "$price_sale" } } },
        { '$set': { 'discount': { '$toDouble': "$discount" } } },
        { '$set': { 'margen': { '$toDouble': "$margen" } } },
        { '$set': { 'iva_value': { '$toDouble': "$iva_value" } } },
        { '$set': { 'price_purchase': { '$toDouble': "$price_purchase" } } },
        { '$set': { 'description': { '$toString': "$description" } } },
        { '$set': { 'root': { '$toString': "$root" } } },
        { '$set': { 'rate': { '$toDouble': "$rate" } } },
        { '$set': { 'quantity': { '$toDouble': "$quantity" } } },
        { '$set': { 'step_unit': { '$toDouble': "$step_unit" } } },
        { '$set': { 'rate_root': { '$toDouble': "$rate_root" } } }
    ]
)