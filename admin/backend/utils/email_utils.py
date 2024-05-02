import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient

client = MongoClient('mongodb://admin:Caremonda@3.23.102.32:27017/frescapp') 
db = client['frescapp']
config = db['orderConfig']  

def send_email(subject, message, to_email,   smtp_username, smtp_password):
    sender_document = config.find_one({}, {'email_sender': 1})
    sender_email = sender_document['email_sender']
    smtp_server = sender_document['smtp_server']
    smtp_port = sender_document['smtp_port']
    smtp_username = sender_document['smtp_username']
    smtp_password = sender_document['smtp_password']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(sender_email, to_email, text)
    server.quit()
