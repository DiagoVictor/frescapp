from flask import Flask, send_file, make_response, request, Response, send_from_directory
from flask_cors import CORS
import os
from api.order_management import order_api
from api.product_management import product_api
from api.customer_management import customer_api
from api.user_management import user_api
from api.config_order import configOrder_api

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

    @app.route('/api/shared/<path:filename>')
    def serve_static(filename):
        root_dir = os.path.dirname(os.getcwd())
        return send_from_directory(os.path.join(root_dir, 'frescapp' , 'admin', 'backend', 'shared','products'), filename)


    # Configurar CORS para permitir solicitudes desde cualquier origen
    CORS(app, resources={"/*": {"origins": "*"}})

    app.run(host='0.0.0.0', port=5000)
