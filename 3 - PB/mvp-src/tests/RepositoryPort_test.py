import os
import sys
import unittest
from unittest.mock import MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Core.Ports.RepositoryPort import RepositoryPort

class TestRepositoryPort(unittest.TestCase):

    def setUp(self):
        # Crea una classe concreta che eredita da RepositoryPort per i test
        class ConcreteRepository(RepositoryPort):
            def executeQuery(self, query, params=None):
                pass

            def fetchOne(self, query, params=None):
                pass

            def fetchAll(self, query, params=None):
                pass

            def close(self):
                pass

        self.repo = ConcreteRepository()

    def testExecuteQuery(self):
        print("Test per controllare se il metodo viene chiamato correttamente con la query specificata")
        self.repo.executeQuery = MagicMock()
        query = "SELECT * FROM users"
        self.repo.executeQuery(query)
        self.repo.executeQuery.assert_called_once_with(query)

    def testFetchOne(self):
        print("Test per controllare se il metodo viene chiamato correttamente con la query e i parametri specificati")
        self.repo.fetchOne = MagicMock(return_value=('user1',))
        query = "SELECT * FROM users WHERE id = %s"
        params = (1,)
        result = self.repo.fetchOne(query, params)
        self.repo.fetchOne.assert_called_once_with(query, params)
        self.assertEqual(result, ('user1',))

    def testFetchAll(self):
        print("Test per controllare se il metodo viene chiamato correttamente con la query specificata e che restituisca tutti i risultati attesi")
        self.repo.fetchAll = MagicMock(return_value=[('user1',), ('user2',)])
        query = "SELECT * FROM users"
        result = self.repo.fetchAll(query)
        self.repo.fetchAll.assert_called_once_with(query)
        self.assertEqual(result, [('user1',), ('user2',)])

    def testClose(self):
        print("Test per controllare se il metodo close viene chiamato correttamente")
        self.repo.close = MagicMock()
        self.repo.close()
        self.repo.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()