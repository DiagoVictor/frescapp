
from flask import Blueprint, jsonify, request

analytics_api = Blueprint('analytics', __name__)

@analytics_api.route('/health')
def health_check():
    return "OK", 200