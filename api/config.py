import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
    AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
    AZURE_CUSTOM_MODEL_ID = os.getenv("AZURE_CUSTOM_MODEL_ID")

    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    CORS_RESOURCES = {
        r"/api/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "http://127.0.0.1:8000",
                "http://localhost:8000"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-Requested-With", "Origin", "Accept"]
        }
    }