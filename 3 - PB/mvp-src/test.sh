#!/bin/bash

# Esegui i test con coverage
# coverage run -m unittest discover -sL tests -p '*_test.py' 
coverage run -m unittest discover -s tests -p '*_integration.py'

# Genera il report di copertura
coverage report