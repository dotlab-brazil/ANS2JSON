import logging
from flask import Flask
from flask_cors import CORS
from config import Config
from routes.digitalizar import digitalizar_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, supports_credentials=True, resources=Config.CORS_RESOURCES)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.info("Inicializando aplicação...")

app.register_blueprint(digitalizar_bp, url_prefix='/api/v1')

@app.route('/health')
def health_check():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)