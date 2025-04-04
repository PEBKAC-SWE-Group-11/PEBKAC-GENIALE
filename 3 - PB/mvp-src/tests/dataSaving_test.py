import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.DataSaving import (
    insertChunksFromLinks,
    insertProductsFromFile,
    insertDocumentsFromLinks,
    writeProductsInDb
)

class TestDataSaving(unittest.TestCase):

    @patch('DataProcessing.DataSaving.processLinksToChunks', return_value=[{'filename': 'file1', 'chunk': 'chunk1', 'vector': [0.1, 0.2, 0.3]}])
    def test_insertChunksFromLinks(self, mock_processLinksToChunks):
        print("Test per la funzione insertChunksFromLinks: Verifica che i chunk vengano inseriti correttamente nel database")
        mock_cursor = MagicMock()
        links = [{'link': 'http://example.com/doc1.pdf'}]
        insertChunksFromLinks(mock_cursor, links)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        mock_cursor.execute.assert_called_with(
            """INSERT INTO Chunk (filename, chunk, embedding) VALUES (%s, %s, %s) ON CONFLICT (filename, chunk) DO NOTHING;""",
            ('file1', 'chunk1', [0.1, 0.2, 0.3])
        )

    @patch('DataProcessing.ProductsElaboration.removeTranslations', return_value=[{'product_id': '1', 'title': 'title1', 'description': 'desc1', 'etim': 'etim1'}])
    @patch('DataProcessing.ProductsElaboration.extractLinks', return_value={'1': {'link': 'http://example.com/doc1.pdf', 'ids': ['1']}})
    @patch('DataProcessing.ProductsElaboration.processProducts', return_value=[{'product_id': '1', 'title': 'title1', 'description': 'desc1', 'etim': 'etim1', 'id_vector': [0.1, 0.2, 0.3], 'idtitle_vector': [0.1, 0.2, 0.3], 'idtitledescr_vector': [0.1, 0.2, 0.3]}])
    @patch('DataProcessing.DataSaving.insertChunksFromLinks')
    @patch('DataProcessing.DataSaving.insertDocumentsFromLinks')
    def test_insertProductsFromFile(self, mock_insertDocumentsFromLinks, mock_insertChunksFromLinks, mock_processProducts, mock_extractLinks, mock_removeTranslations):
        print("Test per la funzione insertProductsFromFile: Verifica che i prodotti vengano elaborati e inseriti correttamente nel database")
        mock_cursor = MagicMock()
        products = [{'product_id': '1', 'title': 'title1', 'description': 'desc1', 'etim': 'etim1'}]
        insertProductsFromFile(mock_cursor, products)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        mock_cursor.execute.assert_called_with(
            """INSERT INTO Product (id, title, description, etim, id_vector, idtitle_vector, idtitledescr_vector) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;""",
            ('1', 'title1', 'desc1', 'etim1', [0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3])
        )

    @patch('re.search', return_value=MagicMock(group=MagicMock(return_value='doc1')))
    def test_insertDocumentsFromLinks(self, mock_re_search):
        print("Test per la funzione insertDocumentsFromLinks: Verifica che i documenti vengano inseriti correttamente nel database")
        mock_cursor = MagicMock()
        links = {'1': {'link': 'http://example.com/doc1.pdf', 'ids': ['1']}}
        insertDocumentsFromLinks(mock_cursor, links)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        mock_cursor.execute.assert_called_with(
            """INSERT INTO Document (title, productId) VALUES (%s, %s) ON CONFLICT (title, productId) DO NOTHING;""",
            ('doc1', '1')
        )

    @patch('builtins.open', new_callable=mock_open, read_data='[{"product_id": "1", "title": "title1", "description": "desc1", "etim": "etim1"}]')
    @patch('json.load', return_value=[{'product_id': '1', 'title': 'title1', 'description': 'desc1', 'etim': 'etim1'}])
    @patch('DataProcessing.DataSaving.insertProductsFromFile')
    @patch('DataProcessing.DataSaving.getDBConnection')
    def test_writeProductsInDb(self, mock_getDBConnection, mock_insertProductsFromFile, mock_json_load, mock_open):
        print("Test per la funzione writeProductsInDb: Verifica che i prodotti vengano letti da un file JSON e scritti correttamente nel database")
        mock_connection = MagicMock()
        mock_getDBConnection.return_value = mock_connection
        writeProductsInDb('products.json', mock_connection)
        mock_open.assert_called_with('products.json', 'r', encoding='utf-8')
        mock_insertProductsFromFile.assert_called_once_with(mock_connection.cursor(), [{'product_id': '1', 'title': 'title1', 'description': 'desc1', 'etim': 'etim1'}])
        mock_connection.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()