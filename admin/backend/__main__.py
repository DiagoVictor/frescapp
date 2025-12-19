from backend.app import app
import os

context = (
    '/etc/letsencrypt/live/app.buyfrescapp.com/fullchain.pem',
    '/etc/letsencrypt/live/app.buyfrescapp.com/privkey.pem'
)
port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port,  ssl_context=context)
