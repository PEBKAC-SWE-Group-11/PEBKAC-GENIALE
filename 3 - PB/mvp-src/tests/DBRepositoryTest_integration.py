import unittest
import psycopg2
from App.Adapters.Repositories.DBRepository import DBRepository

class TestDBRepositoryIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configura la connessione al database di test
        cls.connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )
        cls.cursor = cls.connection.cursor()

        # Crea una tabella di test
        cls.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            );
        ''')
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        # Elimina la tabella di test
        cls.cursor.execute('DROP TABLE IF EXISTS test_table;')
        cls.connection.commit()
        cls.cursor.close()
        cls.connection.close()

    def setUp(self):
        self.repository = DBRepository()
        # Svuota la tabella di test prima di ogni test
        self.repository.executeQuery('DELETE FROM test_table;')

    def tearDown(self):
        self.repository.close()

    def testExecuteQuery(self):
        print("Test di integrazione per il metodo executeQuery: Verifica che una query venga eseguita correttamente")
        query = "INSERT INTO test_table (name) VALUES (%s) RETURNING id;"
        params = ('test_name',)
        cursor = self.repository.executeQuery(query, params)
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertIsInstance(result[0], int)

    def testFetchOne(self):
        print("Test di integrazione per il metodo fetchOne: Verifica che una query venga eseguita correttamente e restituisca un solo risultato")
        query = "INSERT INTO test_table (name) VALUES (%s) RETURNING id;"
        params = ('test_name',)
        self.repository.executeQuery(query, params)

        query = "SELECT * FROM test_table WHERE name = %s;"
        params = ('test_name',)
        result = self.repository.fetchOne(query, params)
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'test_name')

    def testFetchAll(self):
        print("Test di integrazione per il metodo fetchAll: Verifica che una query venga eseguita correttamente e restituisca tutti i risultati")
        query = "INSERT INTO test_table (name) VALUES (%s);"
        params = ('test_name_1',)
        self.repository.executeQuery(query, params)
        params = ('test_name_2',)
        self.repository.executeQuery(query, params)

        query = "SELECT * FROM test_table;"
        results = self.repository.fetchAll(query)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][1], 'test_name_1')
        self.assertEqual(results[1][1], 'test_name_2')

if __name__ == '__main__':
    unittest.main()