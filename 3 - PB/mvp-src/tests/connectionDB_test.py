import unittest
from unittest.mock import patch, MagicMock
import psycopg2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.ConnectionDB import getDBConnection

class TestConnectionDb(unittest.TestCase):

    @patch('psycopg2.connect')
    def testGetDbConnectionSuccess(self, mockConnect):
        print("Test per la funzione getDBConnection: Verifica che la connessione al database venga stabilita correttamente")
        mockConnect.return_value = MagicMock()
        connection = getDBConnection()
        self.assertIsNotNone(connection)
        mockConnect.assert_called_once()

    @patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Connection failed"))
    @patch('time.sleep', return_value=None)
    def testGetDbConnectionFailure(self, mockSleep, mockConnect):
        print("Test per la funzione getDBConnection: Verifica che venga gestito correttamente un errore di connessione al database con tentativi multipli")
        with self.assertRaises(psycopg2.OperationalError):
            getDBConnection()
        self.assertEqual(mockConnect.call_count, 10)
        self.assertEqual(mockSleep.call_count, 9)

if __name__ == '__main__':
    unittest.main()