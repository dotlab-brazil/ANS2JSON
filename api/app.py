import logging
from flask import Flask
from flask import request, make_response
from flask_cors import CORS
from config import Config
from routes.digitalizar import digitalizar_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, supports_credentials=True, resources=Config.CORS_RESOURCES)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.info("Inicializando aplicação...")

app.register_blueprint(digitalizar_bp, url_prefix='/api/v1')

@app.after_request
def add_cors_headers(response):
    # origin = request.headers.get('Origin')
    # allowed = set(Config.CORS_RESOURCES.get(r"/api/*", {}).get("origins", []))
    # if origin and ("*" in allowed or origin in allowed):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Vary'] = 'Origin'
    # response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@app.route('/health')
def health_check():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5051, debug=True)