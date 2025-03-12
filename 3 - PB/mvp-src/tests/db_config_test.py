import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infrastructure.config.db_config import get_database_connection

class TestDBConfig(unittest.TestCase):

    @patch('app.infrastructure.config.db_config.psycopg2.connect')
    def test_get_database_connection(self, mock_connect):
        print("Test per controllare se la connessione al database viene creata correttamente utilizzando psycopg2")
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        connection = get_database_connection()

        mock_connect.assert_called_once_with(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )
        self.assertEqual(connection, mock_connection)

if __name__ == '__main__':
    unittest.main()