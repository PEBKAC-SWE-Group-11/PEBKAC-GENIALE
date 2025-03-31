from flask import Flask
from flask_cors import CORS

flaskApp = Flask(__name__)
CORS(flaskApp, resources={r"/*": {"origins": "http://localhost:4200"}})

if __name__ == '__main__':
    flaskApp.run(host='0.0.0.0', port=5001)