import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.embeddingLocal import getEmbedding
import logging

class TestEmbeddingLocal(unittest.TestCase):

    @patch('requests.post')
    def test_getEmbedding_success(self, mock_post):
        print("Test per la funzione getEmbedding: Verifica che la funzione restituisca correttamente un embedding per un input valido")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_post.return_value = mock_response

        result = getEmbedding("test text")
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_post.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

    @patch('requests.post')
    def test_getEmbedding_failure(self, mock_post):
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un errore del server durante la generazione dell'embedding")
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            getEmbedding("test text")
        self.assertIn("Errore durante la generazione dell'embedding", str(context.exception))
        mock_post.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

    @patch('requests.post', side_effect=Exception("Connection error"))
    def test_getEmbedding_exception(self, mock_post):
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un'eccezione durante la richiesta HTTP")
        with self.assertRaises(Exception) as context:
            getEmbedding("test text")
        self.assertIn("Errore durante la generazione dell'embedding", str(context.exception))
        mock_post.assert_called_once_with(
            "http://app:11434/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": "test text"}
        )

if __name__ == '__main__':
    unittest.main()