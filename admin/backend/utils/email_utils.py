from email.mime.text import MIMEText
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from pymongo import MongoClient
from datetime import datetime
from email.mime.multipart import MIMEMultipart


client = MongoClient('mongodb://admin:Caremonda@3.23.102.32:27017/frescapp') 
db = client['frescapp']
config = db['orderConfig']  

directorio_actual = os.path.dirname(os.path.abspath(__file__))
creds_filename = os.path.join(directorio_actual, 'credenciales.json')

# Alcance del acceso para enviar correos electrónicos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate():
    creds = None
    # Intenta cargar las credenciales desde el archivo JSON
    if os.path.exists('credenciales.json'):
        creds = Credentials.from_authorized_user_file('credenciales.json', SCOPES)
    # Si no hay credenciales válidas disponibles, solicita al usuario que inicie sesión
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guarda las credenciales para la próxima vez
        with open('credenciales.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Autenticar y obtener las credenciales

def create_message(sender, to, subject, html_body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

def send_message( user_id, message, type):
    credentials = authenticate()
    service = build('gmail', 'v1', credentials=credentials)
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        now = datetime.now()  # Obtiene la fecha y hora actuales
        created_at = now.strftime("%Y-%m-%d %H:%M:%S") 
        notification = {
            "created_at" : created_at,
            "type" : type, 
            "message": message
        }
        db.notifications.insert_one(notification)
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None
def send_new_order():
    return ''

def send_restore_password(user_data):
    url = "http://localhost:4200/restore/"+str(user_data.get('user_id'))
    cuerpo = f"""
<!DOCTYPE html>
<html lang="es" style="height: 100%; position: relative;" height="100%">

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>Frescapp</title>
</head>

<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0"
    class="kt-woo-wrap order-items-normal k-responsive-normal title-style-none email-id-new_order"
    style="height: 100%; position: relative; background-color: #f7f7f7; margin: 0; padding: 0;" height="100%"
    backgound-color="#f7f7f7">
    <div id="wrapper" dir="ltr"
        style="background-color: #f7f7f7; margin: 0; padding: 70px 0 70px 0; width: 100%; padding-top: 70px; padding-bottom: px; -webkit-text-size-adjust: none;"
        backgound-color="#f7f7f7" width="100%">
        <table cellpadding="0" cellspacing="0" height="100%" width="100%">
            <tr>
                <td text-align="center" vtext-align="top">
                    <table id="template_header_image_container" style="width: 100%; background-color: transparent;"
                        width="100%" backgound-color="transparent">
                        <tr id="template_header_image">
                            <td text-align="center" vtext-align="middle">
                                <table cellpadding="0" cellspacing="0" width="100%" id="template_header_image_table">
                                    <tr>
                                        <td text-align="center" vtext-align="middle"
                                            style="text-text-align: center; padding-top: 0px; padding-bottom: 0px;">
                                            <p style="margin-bottom: 0; margin-top: 0;"><a
                                                    href="https://www.buyfrescapp.com" target="_blank"
                                                    style="font-weight: normal; color: #97d700; display: block; text-decoration: none;"><img
                                                        src="http://3.23.102.32:5000/api/shared/banner1.png"
                                                        alt="Frescapp" width="600"
                                                        style="border: none; display: inline; font-weight: bold; height: auto; outline: none; text-decoration: none; text-transform: capitalize; font-size: 14px; line-height: 24px; max-width: 100%; width: 600px;"></a>
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <table cellpadding="0" cellspacing="0" width="600" id="template_container"
                        style="background-color: #fff; overflow: hidden; border-style: solid; border-width: 1px; border-right-width: px; border-bottom-width: px; border-left-width: px; border-color: #dedede; border-radius: 3px; box-shadow: 0 1px 4px 1px rgba(0,0,0,.1);"
                        backgound-color="#fff">
                        <tr>
                            <td text-align="center" vtext-align="top">
                                <!-- Header -->
                                <table cellpadding="0" cellspacing="0" width="100%" id="template_header"
                                    style='border-bottom: 0; font-weight: bold; line-height: 100%; vertical-text-align: middle; font-family: "Helvetica Neue",Helvetica,Roboto,Arial,sans-serif; background-color: #97d700; color: #fff;'
                                    backgound-color="#97d700">
                                    <tr>
                                        <td id="header_wrapper"
                                            style="padding: 36px 48px; display: block; text-text-align: left; padding-top: px; padding-bottom: px; padding-left: 48px; padding-right: 48px;"
                                            text-align="left">
                                            <h1
                                                style='margin: 0; text-text-align: left; font-size: 30px; line-height: 40px; font-family: "Helvetica Neue",Helvetica,Roboto,Arial,sans-serif; font-style: normal; font-weight: 300; color: #fff;'>
                                                Para restlabecer tu contraseña por favor da click en el siguiente botón.
                                                <a href="{url}" target="_blank">
                                                    <button style="background-color: white; /* Green */
                                                                    border: none;
                                                                    color: #4CAF50;
                                                                    padding: 15px 32px;
                                                                    text-align: center;
                                                                    text-decoration: none;
                                                                    display: inline-block;
                                                                    font-size: 16px;
                                                                    margin: 4px 2px;
                                                                    cursor: pointer;">
                                                        Ir a cambiar contraseña
                                                    </button>
                                                </a>
                                            </h1>
                                        </td>
                                    </tr>
                                </table>
                                <!-- End Header -->
                            </td>
                        </tr>
                    </table> <!-- End template container -->
                </td>
            </tr>
        </table>
    </div>
</body>

</html>
"""
    message = create_message('Frescapp <fescapp@gmail.com>', user_data.get('email'), 'Restablecer contraseña en Frescapp', cuerpo)
    send_message('me', message,'Reset Password')



