from flask import Flask
from flask_cors import CORS
import sys
import os

flask_app = Flask(__name__)
CORS(flask_app, resources={r"/*": {"origins": "http://localhost:4200"}})

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5001)