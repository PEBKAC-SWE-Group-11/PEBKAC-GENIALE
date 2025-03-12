#!/bin/bash

# Esegui i test con coverage
coverage run -m unittest discover -s tests -p '*_test.py'

# Genera il report di copertura
coverage report