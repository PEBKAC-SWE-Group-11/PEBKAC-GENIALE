import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataProcessing.EmbeddingLocal import getEmbedding
import logging

class TestEmbeddingLocal(unittest.TestCase):

    @patch('requests.post')
    def testGetEmbeddingSuccess(self, mockPost):
        print("Test per la funzione getEmbedding: Verifica che la funzione restituisca correttamente un embedding per un input valido")
        mockResponse = MagicMock()
        mockResponse.status_code = 200
        mockResponse.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mockPost.return_value = mockResponse

        result = getEmbedding("test text")
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mockPost.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

    @patch('requests.post')
    def testGetEmbeddingFailure(self, mockPost):
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un errore del server durante la generazione dell'embedding")
        mockResponse = MagicMock()
        mockResponse.status_code = 500
        mockResponse.text = "Internal Server Error"
        mockPost.return_value = mockResponse

        with self.assertRaises(Exception) as context:
            getEmbedding("test text")
        self.assertIn("Errore durante la generazione dell'embedding", str(context.exception))
        mockPost.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

    @patch('requests.post', side_effect=Exception("Connection error"))
    def testGetEmbeddingException(self, mockPost):
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un'eccezione durante la richiesta HTTP")
        with self.assertRaises(Exception) as context:
            getEmbedding("test text")
        self.assertIn("Errore durante la generazione dell'embedding", str(context.exception))
        mockPost.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

if __name__ == '__main__':
    unittest.main()