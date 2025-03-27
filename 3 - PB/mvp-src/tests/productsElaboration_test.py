# import unittest
# from unittest.mock import patch, MagicMock
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from data_processing.productsElaboration import removeTranslations, extractLinks, processProducts

# class TestProductsElaboration(unittest.TestCase):

#     def test_removeTranslations(self):
#         products = [
#             {
#                 "id": "1",
#                 "documentation": [
#                     "doc1.pdf",
#                     "doc2_FR.pdf",
#                     "doc3.mp4",
#                     "doc4_EN.pdf"
#                 ]
#             }
#         ]
#         expected_output = [
#             {
#                 "id": "1",
#                 "documentation": [
#                     "doc1.pdf"
#                 ]
#             }
#         ]
#         result = removeTranslations(products)
#         self.assertEqual(result, expected_output)

#     def test_extractLinks(self):
#         products = [
#             {
#                 "id": "1",
#                 "documentation": [
#                     "http://example.com/doc1.pdf",
#                     "http://example.com/doc2.pdf"
#                 ]
#             },
#             {
#                 "id": "2",
#                 "documentation": [
#                     "http://example.com/doc1.pdf"
#                 ]
#             }
#         ]
#         expected_output = {
#             "http://example.com/doc1.pdf": {"link": "http://example.com/doc1.pdf", "ids": ["1", "2"]},
#             "http://example.com/doc2.pdf": {"link": "http://example.com/doc2.pdf", "ids": ["1"]}
#         }
#         result = extractLinks(products)
#         self.assertEqual(result, expected_output)

#     @patch('..data_processing.productsElaboration.getEmbedding', return_value=[0.1, 0.2, 0.3])
#     def test_processProducts(self, mock_getEmbedding):
#         products = [
#             {
#                 "id": "1",
#                 "title": "Product 1",
#                 "description": "Description 1",
#                 "technical_data": {"weight": "1kg"},
#                 "price": "10"
#             }
#         ]
#         expected_output = [
#             {
#                 "product_id": "1",
#                 "title": "Product 1",
#                 "description": "Description 1",
#                 "etim": "id: 1, weight: 1kg, price: 10",
#                 "id_vector": [0.1, 0.2, 0.3],
#                 "idtitle_vector": [0.1, 0.2, 0.3],
#                 "idtitledescr_vector": [0.1, 0.2, 0.3]
#             }
#         ]
#         result = processProducts(products)
#         self.assertEqual(result, expected_output)
#         mock_getEmbedding.assert_called()

# if __name__ == '__main__':
#     unittest.main()