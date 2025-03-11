import sys
import os

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Usa import assoluti
from app.infrastructure.http.api import app
import app.adapters.controllers.api_controller

print("Imports successful")