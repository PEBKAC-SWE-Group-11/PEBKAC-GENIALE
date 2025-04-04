import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Infrastructure.Config.DBConfig import getDatabaseConnection

class TestDBConfig(unittest.TestCase):

    @patch('App.Infrastructure.Config.DBConfig.psycopg2.connect')
    def testGetDatabaseConnection(self, mockConnect):
        print("Test per controllare se la connessione al database viene creata correttamente utilizzando psycopg2")
        mockConnection = MagicMock()
        mockConnect.return_value = mockConnection

        connection = getDatabaseConnection()

        mockConnect.assert_called_once_with(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )
        self.assertEqual(connection, mockConnection)

if __name__ == '__main__':
    unittest.main()