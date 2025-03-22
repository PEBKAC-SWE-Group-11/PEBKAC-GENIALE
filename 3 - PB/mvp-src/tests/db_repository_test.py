import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.adapters.repositories.db_repository import DBRepository

class TestDBRepository(unittest.TestCase):

    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        self.mock_connection = MagicMock()
        mock_connect.return_value = self.mock_connection
        self.repo = DBRepository()

    def test_execute_query(self):
        print("Test per controllare se una query viene eseguita correttamente")
        mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = mock_cursor

        query = "SELECT * FROM users"
        self.repo.execute_query(query)

        self.mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(query, None)
        self.mock_connection.commit.assert_called_once()

    def test_fetch_one(self):
        print("Test per controllare se una query viene eseguita correttamente e restituisce un solo risultato")
        mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('user1',)

        query = "SELECT * FROM users WHERE id = %s"
        params = (1,)
        result = self.repo.fetch_one(query, params)

        self.assertEqual(result, ('user1',))
        self.mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(query, params)
        self.mock_connection.commit.assert_called_once()

    def test_fetch_all(self):
        print("Test per controllare se una query viene eseguita correttamente e restituisce tutti i risultati")
        mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('user1',), ('user2',)]

        query = "SELECT * FROM users"
        result = self.repo.fetch_all(query)

        self.assertEqual(result, [('user1',), ('user2',)])
        self.mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(query, None)
        self.mock_connection.commit.assert_called_once()

    def test_close(self):
        print("Test per controllare se la connessione al database viene chiusa correttamente")
        self.repo.close()
        self.mock_connection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()