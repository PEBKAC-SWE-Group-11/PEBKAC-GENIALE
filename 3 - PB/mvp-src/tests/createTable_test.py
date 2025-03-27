import unittest
from unittest.mock import patch, MagicMock
from psycopg2.extensions import connection as pgConnection
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.createTable import createTables, getVectorDimension


class TestCreateTable(unittest.TestCase):

    @patch('data_processing.createTable.getEmbedding', return_value=[0.1, 0.2, 0.3])
    def test_getVectorDimension(self, mock_getEmbedding):
        dimension = getVectorDimension()
        self.assertEqual(dimension, 3)
        mock_getEmbedding.assert_called_once_with("test")

    @patch('..data_processing.createTable.getVectorDimension', return_value=3)
    @patch('..data_processing.createTable.pgConnection')
    def test_createTables(self, mock_getVectorDimension, mock_pgConnection):
        mock_cursor = MagicMock()
        mock_pgConnection.cursor.return_value = mock_cursor

        createTables(mock_pgConnection)

        self.assertEqual(mock_cursor.execute.call_count, 9)  # 7 tables + 1 trigger creation + 1 trigger function
        mock_pgConnection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()