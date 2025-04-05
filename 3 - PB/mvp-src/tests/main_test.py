import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.Main import initDB, importData, main

class TestMain(unittest.TestCase):

    @patch('DataProcessing.Main.createTables')
    def testInitDbSuccess(self, mockCreateTables):
        print("Test per la funzione initDB: Verifica che le tabelle vengano create correttamente nel database")
        mockConnection = MagicMock()
        initDB(mockConnection)
        mockCreateTables.assert_called_once_with(mockConnection)

    @patch('DataProcessing.Main.createTables', side_effect=Exception("DB Error"))
    def testInitDbFailure(self, mockCreateTables):
        print("Test per la funzione initDB: Verifica che venga gestito correttamente un errore durante la creazione delle tabelle")
        mockConnection = MagicMock()
        with self.assertRaises(Exception) as context:
            initDB(mockConnection)
        self.assertIn("DB Error", str(context.exception))
        mockCreateTables.assert_called_once_with(mockConnection)

    @patch('DataProcessing.Main.writeProductsInDb')
    def testImportDataSuccess(self, mockWriteProductsInDb):
        print("Test per la funzione importData: Verifica che i dati vengano importati correttamente nel database")
        mockConnection = MagicMock()
        jsonPath = "path/to/json"
        importData(mockConnection, jsonPath)
        mockWriteProductsInDb.assert_called_once_with(jsonPath, mockConnection)

    @patch('DataProcessing.Main.writeProductsInDb', side_effect=Exception("Import Error"))
    def testImportDataFailure(self, mockWriteProductsInDb):
        print("Test per la funzione importData: Verifica che venga gestito correttamente un errore durante l'importazione dei dati")
        mockConnection = MagicMock()
        jsonPath = "path/to/json"
        with self.assertRaises(Exception) as context:
            importData(mockConnection, jsonPath)
        self.assertIn("Import Error", str(context.exception))
        mockWriteProductsInDb.assert_called_once_with(jsonPath, mockConnection)

    @patch('DataProcessing.Main.getDBConnection')
    @patch('DataProcessing.Main.initDB')
    @patch('DataProcessing.Main.importData')
    def testMainSuccess(self, mockImportData, mockInitDb, mockGetDbConnection):
        print("Test per la funzione main: Verifica che il flusso principale venga eseguito correttamente")
        mockConnection = MagicMock()
        mockGetDbConnection.return_value = mockConnection
        with patch('os.path.join', return_value='jsonData/data.json'):
            main()
        mockGetDbConnection.assert_called_once()
        mockInitDb.assert_called_once_with(mockConnection)
        mockImportData.assert_called_once_with(mockConnection, 'jsonData/data.json')
        mockConnection.close.assert_called_once()

    @patch('DataProcessing.Main.getDBConnection', side_effect=Exception("Connection Error"))
    def testMainFailure(self, mockGetDbConnection):
        print("Test per la funzione main: Verifica che venga gestito correttamente un errore durante la connessione al database")
        with self.assertRaises(Exception) as context:
            main()
        self.assertIn("Connection Error", str(context.exception))
        mockGetDbConnection.assert_called_once()

if __name__ == '__main__':
    unittest.main()