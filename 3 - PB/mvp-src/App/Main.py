import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Infrastructure.Http.API import flaskApp
from App.Adapters.Controllers import APIController  

if __name__ == '__main__':
    flaskApp.run(host='0.0.0.0', port=5001)