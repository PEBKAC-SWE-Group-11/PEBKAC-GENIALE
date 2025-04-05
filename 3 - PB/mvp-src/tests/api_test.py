import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Infrastructure.Http.API import flaskApp

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = flaskApp.test_client()
        self.app.testing = True

    def testCorsHeaders(self):
        print("Test per verificare gli header CORS:")
        response = self.app.get('/api/test')
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], 'http://localhost:4200')

if __name__ == '__main__':
    unittest.main()