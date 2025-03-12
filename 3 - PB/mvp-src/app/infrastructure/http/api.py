from flask import Flask
from flask_cors import CORS
import sys
import os

flask_app = Flask(__name__)
CORS(flask_app, resources={r"/*": {"origins": "http://localhost:4200"}})

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importa il controller per registrare le route
import app.adapters.controllers.api_controller

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5001)