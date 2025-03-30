import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import BytesIO
from pypdf import PdfWriter
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.chunkElabotation import createDirectories, pdfToTxt, downloadPdf, processPdf, splitIntoChunks, processTextToChunks

class TestChunkElabotation(unittest.TestCase):

    @patch('os.makedirs')
    def test_createDirectories(self, mock_makedirs):
        print("Test per la funzione createDirectories: Verifica che vengano create correttamente le directory necessarie")
        createDirectories()
        mock_makedirs.assert_any_call('pdfs', exist_ok=True)
        mock_makedirs.assert_any_call('txts', exist_ok=True)

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_downloadPdf(self, mock_open_file, mock_requests_get):
        print("Test per la funzione downloadPdf: Verifica che un PDF venga scaricato correttamente e salvato")
        mock_response = MagicMock()
        mock_response.iter_content = MagicMock(return_value=[b'data'])
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        result = downloadPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'sample.pdf')
        self.assertTrue(result)
        mock_open_file.assert_called_with('sample.pdf', 'wb')
        mock_open_file().write.assert_called_with(b'data')

    @patch('requests.get')
    def test_downloadPdf_failure(self, mock_requests_get):
        print("Test per la funzione downloadPdf: Verifica che il download fallisca correttamente in caso di errore HTTP")
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        result = downloadPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'sample.pdf')
        self.assertFalse(result)

    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))  # Simula il comportamento di os.path.join
    @patch('os.path.basename', return_value='sample.pdf')
    @patch('builtins.print')
    @patch('data_processing.chunkElabotation.downloadPdf', return_value=True)
    @patch('data_processing.chunkElabotation.pdfToTxt')
    def test_processPdf(self, mock_pdfToTxt, mock_downloadPdf, mock_print, mock_basename, mock_join):
        print("Test per la funzione processPdf: Verifica che un PDF venga scaricato e convertito correttamente in un file di testo")
        result = processPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf')
        self.assertEqual(result, 'txts/sample.txt')
        mock_downloadPdf.assert_called_once_with('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'pdfs/sample.pdf')
        mock_pdfToTxt.assert_called_once_with('pdfs/sample.pdf', 'txts/sample.txt')

    @patch('builtins.open', new_callable=mock_open, read_data="This is a sample text for testing.")
    @patch('data_processing.chunkElabotation.getEmbedding', return_value=[0.1, 0.2, 0.3])
    def test_processTextToChunks(self, mock_getEmbedding, mock_open_file):
        print("Test per la funzione processTextToChunks: Verifica che un file di testo venga suddiviso in chunk e che vengano generati i relativi vettori di embedding")
        result = processTextToChunks('sample.txt')
        expected_result = [{
            "filename": "sample",
            "chunk": "This is a sample text for testing.",
            "vector": [0.1, 0.2, 0.3]
        }]
        self.assertEqual(result, expected_result)
        mock_open_file.assert_called_with('sample.txt', 'r', encoding='utf-8')
        mock_getEmbedding.assert_called_once_with("This is a sample text for testing.")

if __name__ == '__main__':
    unittest.main()