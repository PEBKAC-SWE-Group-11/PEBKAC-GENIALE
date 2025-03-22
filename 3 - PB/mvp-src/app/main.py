import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.http.api import flask_app
from app.adapters.controllers import api_controller  

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5001)