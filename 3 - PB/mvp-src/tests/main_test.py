import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.main import initDB, importData, main

class TestMain(unittest.TestCase):

    @patch('data_processing.main.createTables')
    def test_initDB_success(self, mock_createTables):
        print("Test per la funzione initDB: Verifica che le tabelle vengano create correttamente nel database")
        mock_connection = MagicMock()
        initDB(mock_connection)
        mock_createTables.assert_called_once_with(mock_connection)

    @patch('data_processing.main.createTables', side_effect=Exception("DB Error"))
    def test_initDB_failure(self, mock_createTables):
        print("Test per la funzione initDB: Verifica che venga gestito correttamente un errore durante la creazione delle tabelle")
        mock_connection = MagicMock()
        with self.assertRaises(Exception) as context:
            initDB(mock_connection)
        self.assertIn("DB Error", str(context.exception))
        mock_createTables.assert_called_once_with(mock_connection)

    @patch('data_processing.main.writeProductsInDb')
    def test_importData_success(self, mock_writeProductsInDb):
        print("Test per la funzione importData: Verifica che i dati vengano importati correttamente nel database")
        mock_connection = MagicMock()
        jsonPath = "path/to/json"
        importData(mock_connection, jsonPath)
        mock_writeProductsInDb.assert_called_once_with(jsonPath, mock_connection)

    @patch('data_processing.main.writeProductsInDb', side_effect=Exception("Import Error"))
    def test_importData_failure(self, mock_writeProductsInDb):
        print("Test per la funzione importData: Verifica che venga gestito correttamente un errore durante l'importazione dei dati")
        mock_connection = MagicMock()
        jsonPath = "path/to/json"
        with self.assertRaises(Exception) as context:
            importData(mock_connection, jsonPath)
        self.assertIn("Import Error", str(context.exception))
        mock_writeProductsInDb.assert_called_once_with(jsonPath, mock_connection)

    @patch('data_processing.main.getDBConnection')
    @patch('data_processing.main.initDB')
    @patch('data_processing.main.importData')
    def test_main_success(self, mock_importData, mock_initDB, mock_getDBConnection):
        print("Test per la funzione main: Verifica che il flusso principale venga eseguito correttamente")
        mock_connection = MagicMock()
        mock_getDBConnection.return_value = mock_connection
        with patch('os.path.join', return_value='jsonData/data.json'):
            main()
        mock_getDBConnection.assert_called_once()
        mock_initDB.assert_called_once_with(mock_connection)
        mock_importData.assert_called_once_with(mock_connection, 'jsonData/data.json')
        mock_connection.close.assert_called_once()

    @patch('data_processing.main.getDBConnection', side_effect=Exception("Connection Error"))
    def test_main_failure(self, mock_getDBConnection):
        print("Test per la funzione main: Verifica che venga gestito correttamente un errore durante la connessione al database")
        with self.assertRaises(Exception) as context:
            main()
        self.assertIn("Connection Error", str(context.exception))
        mock_getDBConnection.assert_called_once()

if __name__ == '__main__':
    unittest.main()