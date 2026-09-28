from backend.app import app
import os
from flask_cors import CORS


port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    if os.getenv("FLASK_ENV") == "production":
        print("🔒 Modo producción: Usando SSL/TLS")
        context = (
        '/etc/letsencrypt/live/app.buyfrescapp.com/fullchain.pem',
        '/etc/letsencrypt/live/app.buyfrescapp.com/privkey.pem'
    )
        CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
        app.run(host='0.0.0.0', port=port, ssl_context=context)
    else:
        print("⚠️ Modo desarrollo: No se está usando SSL/TLS")
        app.run(host='0.0.0.0', port=port)
