import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Scope para enviar correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Ajusta esta ruta
PATH = 'C:/Users/Usuario/Documents/frescapp/admin/backend/utils/'

CLIENT_SECRET_FILE = os.path.join(PATH, 'client_secret.json')
TOKEN_FILE = os.path.join(PATH, 'credentials.json')


def generate_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    # Esto abre el navegador
    creds = flow.run_local_server(port=0)

    # Guardar credenciales
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    print("✅ Credenciales generadas en:", TOKEN_FILE)


if __name__ == "__main__":
    generate_credentials()