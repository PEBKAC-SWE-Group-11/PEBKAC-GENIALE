import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.ProductsElaboration import removeTranslations, extractLinks, processProducts

class TestProductsElaboration(unittest.TestCase):

    def testRemoveTranslations(self):
        print("Test per la funzione removeTranslations: Verifica che i documenti tradotti vengano rimossi correttamente dai prodotti")
        products = [
            {
                "id": "1",
                "documentation": [
                    "doc1.pdf",
                    "doc2_FR.pdf",
                    "doc3.mp4",
                    "doc4_EN.pdf"
                ]
            }
        ]
        expectedOutput = [
            {
                "id": "1",
                "documentation": [
                    "doc1.pdf"
                ]
            }
        ]
        result = removeTranslations(products)
        self.assertEqual(result, expectedOutput)

    def testExtractLinks(self):
        print("Test per la funzione extractLinks: Verifica che i link vengano estratti correttamente dai prodotti e raggruppati per ID")
        products = [
            {
                "id": "1",
                "documentation": [
                    "http://example.com/doc1.pdf",
                    "http://example.com/doc2.pdf"
                ]
            },
            {
                "id": "2",
                "documentation": [
                    "http://example.com/doc1.pdf"
                ]
            }
        ]
        expectedOutput = {
            "http://example.com/doc1.pdf": {"link": "http://example.com/doc1.pdf", "ids": ["1", "2"]},
            "http://example.com/doc2.pdf": {"link": "http://example.com/doc2.pdf", "ids": ["1"]}
        }
        result = extractLinks(products)
        self.assertEqual(result, expectedOutput)

    @patch('DataProcessing.ProductsElaboration.getEmbedding', return_value=[0.1, 0.2, 0.3])
    def testProcessProducts(self, mockGetEmbedding):
        print("Test per la funzione processProducts: Verifica che i prodotti vengano elaborati correttamente e che vengano generati i vettori di embedding")
        products = [
            {
                "id": "1",
                "title": "Product 1",
                "description": "Description 1",
                "technical_data": {"weight": "1kg"},
                "price": "10"
            }
        ]
        expectedOutput = [
            {
                "productId": "1",
                "title": "Product 1",
                "description": "Description 1",
                "etim": "id: 1, weight: 1kg, price: 10",
                "idVector": [0.1, 0.2, 0.3],
                "idTitleVector": [0.1, 0.2, 0.3],
                "idTitleDescrVector": [0.1, 0.2, 0.3]
            }
        ]
        result = processProducts(products)
        self.assertEqual(result, expectedOutput)
        mockGetEmbedding.assert_called()

if __name__ == '__main__':
    unittest.main()