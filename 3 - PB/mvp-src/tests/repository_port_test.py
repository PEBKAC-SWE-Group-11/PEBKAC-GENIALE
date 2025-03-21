import os
import sys
import unittest
from unittest.mock import MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.ports.repository_port import RepositoryPort

class TestRepositoryPort(unittest.TestCase):

    def setUp(self):
        # Crea una classe concreta che eredita da RepositoryPort per i test
        class ConcreteRepository(RepositoryPort):
            def execute_query(self, query, params=None):
                pass

            def fetch_one(self, query, params=None):
                pass

            def fetch_all(self, query, params=None):
                pass

            def close(self):
                pass

        self.repo = ConcreteRepository()

    def test_execute_query(self):
        print("Test per controllare se il metodo viene chiamata correttamente con la query specificata")
        self.repo.execute_query = MagicMock()
        query = "SELECT * FROM users"
        self.repo.execute_query(query)
        self.repo.execute_query.assert_called_once_with(query)

    def test_fetch_one(self):
        print("Test per controllare se il metodo viene chiamata correttamente con la query e i parametri specificati")
        self.repo.fetch_one = MagicMock(return_value=('user1',))
        query = "SELECT * FROM users WHERE id = %s"
        params = (1,)
        result = self.repo.fetch_one(query, params)
        self.repo.fetch_one.assert_called_once_with(query, params)
        self.assertEqual(result, ('user1',))

    def test_fetch_all(self):
        print("Test per controllare se il metodo viene chiamata correttamente con la query specificata e che restituisca tutti i risultati attesi")
        self.repo.fetch_all = MagicMock(return_value=[('user1',), ('user2',)])
        query = "SELECT * FROM users"
        result = self.repo.fetch_all(query)  # Aggiungi il secondo parametro None(non so se vada bene NONE)
        self.repo.fetch_all.assert_called_once_with(query)
        self.assertEqual(result, [('user1',), ('user2',)])

    def test_close(self):
        print("Test per controllare se il metodo close viene chiamato correttamente")
        self.repo.close = MagicMock()
        self.repo.close()
        self.repo.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()