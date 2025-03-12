import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.http.api import flask_app

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    def test_cors_headers(self):
        print("Headers CORS Test:")
        response = self.app.get('/')
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'http://localhost:4200')

    def test_root_endpoint(self):
        print("Endpoint Root Test:")
        response = self.app.get('/')
        self.assertEqual(response.status_code, 404)  # Assuming there's no root endpoint defined

if __name__ == '__main__':
    unittest.main()