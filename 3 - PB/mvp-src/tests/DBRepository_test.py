import sys
import os
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Adapters.Repositories.DBRepository import DBRepository

class TestDBRepository(unittest.TestCase):

    @patch('psycopg2.connect')
    def setUp(self, mockConnect):
        self.mockConnection = MagicMock()
        mockConnect.return_value = self.mockConnection
        self.repo = DBRepository()

    def testExecuteQuery(self):
        print("Test per controllare se una query viene eseguita correttamente")
        mockCursor = MagicMock()
        self.mockConnection.cursor.return_value = mockCursor

        query = "SELECT * FROM users"
        self.repo.executeQuery(query)

        self.mockConnection.cursor.assert_called_once()
        mockCursor.execute.assert_called_once_with(query, None)
        self.mockConnection.commit.assert_called_once()

    def testFetchOne(self):
        print("Test per controllare se una query viene eseguita correttamente e restituisce un solo risultato")
        mockCursor = MagicMock()
        self.mockConnection.cursor.return_value = mockCursor
        mockCursor.fetchone.return_value = ('user1',)

        query = "SELECT * FROM users WHERE id = %s"
        params = (1,)
        result = self.repo.fetchOne(query, params)

        self.assertEqual(result, ('user1',))
        self.mockConnection.cursor.assert_called_once()
        mockCursor.execute.assert_called_once_with(query, params)
        self.mockConnection.commit.assert_called_once()

    def testFetchAll(self):
        print("Test per controllare se una query viene eseguita correttamente e restituisce tutti i risultati")
        mockCursor = MagicMock()
        self.mockConnection.cursor.return_value = mockCursor
        mockCursor.fetchall.return_value = [('user1',), ('user2',)]

        query = "SELECT * FROM users"
        result = self.repo.fetchAll(query)

        self.assertEqual(result, [('user1',), ('user2',)])
        self.mockConnection.cursor.assert_called_once()
        mockCursor.execute.assert_called_once_with(query, None)
        self.mockConnection.commit.assert_called_once()

    def testClose(self):
        print("Test per controllare se la connessione al database viene chiusa correttamente")
        self.repo.close()
        self.mockConnection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()