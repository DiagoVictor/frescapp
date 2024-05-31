from flask import Blueprint, jsonify, request, send_file, Response
from models.order import Order
import json
from flask_bcrypt import Bcrypt
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import locale
from flask import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from io import BytesIO
from utils.email_utils import send_new_order  # Importa la función send_email que creamos antes
from io import StringIO
import csv

purchase_api = Blueprint('purchase', __name__)

@purchase_api.route('/purchase', methods=['POST'])
def create_purchase():
    None