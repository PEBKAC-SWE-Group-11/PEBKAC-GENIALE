# import unittest
# from unittest.mock import patch, mock_open, MagicMock
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from data_processing.chunkElabotation import createDirectories, pdfToTxt, downloadPdf, processPdf, splitIntoChunks, processTextToChunks

# class TestChunkElabotation(unittest.TestCase):

#     @patch('os.makedirs')
#     def test_createDirectories(self, mock_makedirs):
#         createDirectories()
#         mock_makedirs.assert_any_call('pdfs', exist_ok=True)
#         mock_makedirs.assert_any_call('txts', exist_ok=True)

#     @patch('builtins.open', new_callable=mock_open)
#     @patch('pypdf.PdfReader')
#     def test_pdfToTxt(self, mock_pdf_reader, mock_open_file):
#         mock_pdf_reader.return_value.pages = [MagicMock(extract_text=MagicMock(return_value='Sample text'))]
#         pdfToTxt('sample.pdf', 'sample.txt')
#         mock_open_file.assert_called_with('sample.txt', 'w', encoding='utf-8')
#         mock_open_file().write.assert_called_with('Sample text')

#     @patch('requests.get')
#     @patch('builtins.open', new_callable=mock_open)
#     def test_downloadPdf(self, mock_open_file, mock_requests_get):
#         mock_response = MagicMock()
#         mock_response.iter_content = MagicMock(return_value=[b'data'])
#         mock_response.status_code = 200
#         mock_requests_get.return_value = mock_response

#         result = downloadPdf('http://example.com/sample.pdf', 'sample.pdf')
#         self.assertTrue(result)
#         mock_open_file.assert_called_with('sample.pdf', 'wb')
#         mock_open_file().write.assert_called_with(b'data')

#     @patch('requests.get')
#     def test_downloadPdf_failure(self, mock_requests_get):
#         mock_response = MagicMock()
#         mock_response.status_code = 404
#         mock_requests_get.return_value = mock_response

#         result = downloadPdf('http://example.com/sample.pdf', 'sample.pdf')
#         self.assertFalse(result)

#     @patch('os.path.join', return_value='sample.pdf')
#     @patch('os.path.basename', return_value='sample.pdf')
#     @patch('builtins.print')
#     @patch('..data_processing.chunkElabotation.downloadPdf', return_value=True)
#     @patch('..data_processing.chunkElabotation.pdfToTxt')
#     def test_processPdf(self, mock_pdfToTxt, mock_downloadPdf, mock_print, mock_basename, mock_join):
#         result = processPdf('http://example.com/sample.pdf')
#         self.assertEqual(result, 'txts/sample.txt')
#         mock_downloadPdf.assert_called_once_with('http://example.com/sample.pdf', 'sample.pdf')
#         mock_pdfToTxt.assert_called_once_with('sample.pdf', 'txts/sample.txt')

#     def test_splitIntoChunks(self):
#         text = "This is a sample text for testing splitIntoChunks function."
#         chunks = splitIntoChunks(text, 10, 2)
#         expected_chunks = [
#             "This is a sample",
#             "is a sample text",
#             "a sample text for",
#             "sample text for testing",
#             "text for testing splitIntoChunks",
#             "for testing splitIntoChunks function.",
#             "testing splitIntoChunks function."
#         ]
#         self.assertEqual(chunks, expected_chunks)

#     @patch('builtins.open', new_callable=mock_open, read_data="This is a sample text for testing.")
#     @patch('..data_processing.chunkElabotation.getEmbedding', return_value=[0.1, 0.2, 0.3])
#     def test_processTextToChunks(self, mock_getEmbedding, mock_open_file):
#         result = processTextToChunks('sample.txt')
#         expected_result = [{
#             "filename": "sample",
#             "chunk": "This is a sample text for testing.",
#             "vector": [0.1, 0.2, 0.3]
#         }]
#         self.assertEqual(result, expected_result)
#         mock_open_file.assert_called_with('sample.txt', 'r', encoding='utf-8')
#         mock_getEmbedding.assert_called_once_with("This is a sample text for testing.")

# if __name__ == '__main__':
#     unittest.main()