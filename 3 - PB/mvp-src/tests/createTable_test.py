import unittest
from unittest.mock import patch, MagicMock
from psycopg2.extensions import connection as pgConnection
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.CreateTable import createTables, getVectorDimension


class TestCreateTable(unittest.TestCase):

    @patch('DataProcessing.CreateTable.getEmbedding', return_value=[0.1, 0.2, 0.3])
    def testGetVectorDimension(self, mockGetEmbedding):
        print("Test per la funzione getVectorDimension: Verifica che la funzione calcoli correttamente la dimensione del vettore di embedding")
        dimension = getVectorDimension()
        self.assertEqual(dimension, 1024)  # Aggiornato per riflettere il valore attuale
        mockGetEmbedding.assert_not_called()  # La funzione non chiama più getEmbedding

    @patch('DataProcessing.CreateTable.getVectorDimension', return_value=3)
    @patch('DataProcessing.CreateTable.pgConnection')
    def testCreateTables(self, mockGetVectorDimension, mockPgConnection):
        print("Test per la funzione createTables: Verifica che vengano create correttamente le tabelle e i trigger nel database")
        mockCursor = MagicMock()
        mockPgConnection.cursor.return_value = mockCursor

        createTables(mockPgConnection)

        self.assertEqual(mockCursor.execute.call_count, 8)  # 7 tables + 1 trigger creation + 1 trigger function
        mockPgConnection.commit.assert_called_once()
        mockCursor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()