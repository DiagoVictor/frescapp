from flask import Flask, send_file, make_response, request, Response, send_from_directory
from flask_cors import CORS
import os
from api.order_management import order_api
from api.product_management import product_api
from api.customer_management import customer_api
from api.user_management import user_api
from api.config_order import configOrder_api
from api.reports_management import report_api
from api.discount_management import discount_api
from api.alegra_management import alegra_api
from api.woo_management import woo_api
from api.purchase_management import purchase_api
from api.action_management import action_api
from api.supplier_management import supplier_api


if __name__ == '__main__':
    app = Flask(__name__)
    # Configura la aplicación utilizando el archivo config.py
    app.config.from_pyfile('config.py')

    # Token secreto para autenticación

    # Registra los blueprints de los diferentes módulos de la aplicación
    app.register_blueprint(order_api, url_prefix='/api/order')
    app.register_blueprint(product_api, url_prefix='/api/product')
    app.register_blueprint(customer_api, url_prefix='/api/customer')
    app.register_blueprint(user_api, url_prefix='/api/user')
    app.register_blueprint(configOrder_api, url_prefix='/api/config')
    app.register_blueprint(report_api, url_prefix='/api/reports')
    app.register_blueprint(discount_api, url_prefix='/api/discount')
    app.register_blueprint(alegra_api, url_prefix='/api/alegra')
    app.register_blueprint(woo_api, url_prefix='/api/woo')
    app.register_blueprint(purchase_api, url_prefix='/api/purchase')
    app.register_blueprint(action_api, url_prefix='/api/action')
    app.register_blueprint(supplier_api, url_prefix='/api/supplier')

    @app.route('/api/shared/<path:filename>')
    def serve_static(filename):
        root_dir = os.path.dirname(os.getcwd())
        file_path = os.path.join(root_dir, 'backend', 'shared', 'products', filename)
        
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(root_dir, 'backend', 'shared', 'products'), filename)
        else:
            # Si el archivo no existe, envía sin_foto.png
            return send_from_directory(os.path.join(root_dir, 'backend', 'shared'), 'sin_foto.png')


    # Configurar CORS para permitir solicitudes desde cualquier origen
    CORS(app, resources={"/*": {"origins": "*"}})
    context = ('/etc/ssl/certs/app_buyfrescapp_com.crt', '/etc/ssl/certs/app_buyfrescapp_com.key')

    app.run(host='0.0.0.0', port=5000, ssl_context=context)