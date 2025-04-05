import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import BytesIO
from pypdf import PdfWriter
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.ChunkElaboration import createDirectories, pdfToTxt, downloadPdf, processPdf, splitIntoChunks, processTextToChunks

class TestChunkElaboration(unittest.TestCase):

    @patch('os.makedirs')
    def testCreateDirectories(self, mockMakedirs):
        print("Test per la funzione createDirectories: Verifica che vengano create correttamente le directory necessarie")
        createDirectories()
        mockMakedirs.assert_any_call('pdfs', exist_ok=True)
        mockMakedirs.assert_any_call('txts', exist_ok=True)

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def testDownloadPdf(self, mockOpenFile, mockRequestsGet):
        print("Test per la funzione downloadPdf: Verifica che un PDF venga scaricato correttamente e salvato")
        mockResponse = MagicMock()
        mockResponse.iter_content = MagicMock(return_value=[b'data'])
        mockResponse.status_code = 200
        mockRequestsGet.return_value = mockResponse

        result = downloadPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'sample.pdf')
        self.assertTrue(result)
        mockOpenFile.assert_called_with('sample.pdf', 'wb')
        mockOpenFile().write.assert_called_with(b'data')

    @patch('requests.get')
    def testDownloadPdfFailure(self, mockRequestsGet):
        print("Test per la funzione downloadPdf: Verifica che il download fallisca correttamente in caso di errore HTTP")
        mockResponse = MagicMock()
        mockResponse.status_code = 404
        mockRequestsGet.return_value = mockResponse

        result = downloadPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'sample.pdf')
        self.assertFalse(result)

    @patch('os.path.join', side_effect=lambda *args: '/'.join(args))  # Simula il comportamento di os.path.join
    @patch('os.path.basename', return_value='sample.pdf')
    @patch('builtins.print')
    @patch('DataProcessing.ChunkElaboration.downloadPdf', return_value=True)
    @patch('DataProcessing.ChunkElaboration.pdfToTxt')
    def testProcessPdf(self, mockPdfToTxt, mockDownloadPdf, mockPrint, mockBasename, mockJoin):
        print("Test per la funzione processPdf: Verifica che un PDF venga scaricato e convertito correttamente in un file di testo")
        result = processPdf('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf')
        self.assertEqual(result, 'txts/sample.txt')
        mockDownloadPdf.assert_called_once_with('sample.pdf/irj/go/km/docs/z_catalogo/DOCUMENT/ZIS_49401771A0_FI.100294.pdf', 'pdfs/sample.pdf')
        mockPdfToTxt.assert_called_once_with('pdfs/sample.pdf', 'txts/sample.txt')

    @patch('builtins.open', new_callable=mock_open, read_data="This is a sample text for testing.")
    @patch('DataProcessing.ChunkElaboration.getEmbedding', return_value=[0.1, 0.2, 0.3])
    def testProcessTextToChunks(self, mockGetEmbedding, mockOpenFile):
        print("Test per la funzione processTextToChunks: Verifica che un file di testo venga suddiviso in chunk e che vengano generati i relativi vettori di embedding")
        result = processTextToChunks('sample.txt')
        expectedResult = [{
            "filename": "sample",
            "chunk": "This is a sample text for testing.",
            "vector": [0.1, 0.2, 0.3]
        }]
        self.assertEqual(result, expectedResult)
        mockOpenFile.assert_called_with('sample.txt', 'r', encoding='utf-8')
        mockGetEmbedding.assert_called_once_with("This is a sample text for testing.")

if __name__ == '__main__':
    unittest.main()