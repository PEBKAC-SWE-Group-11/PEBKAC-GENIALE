import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from app.adapters.services.embedding_service import EmbeddingService, OLLAMA_EMBED_URL

class TestEmbeddingService(unittest.TestCase):

    @patch('app.adapters.services.embedding_service.requests.post')
    def test_get_embeddings_success(self, mock_post):
        print("Test per controllare se viene generato correttamente un embedding per una query quando la richiesta HTTP ha successo")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_post.return_value = mock_response

        service = EmbeddingService()
        prompt = "test prompt"
        result = service.get_embeddings(prompt)

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_post.assert_called_once_with(OLLAMA_EMBED_URL, json={"model": "nomic-embed-text", "prompt": prompt})

    @patch('app.adapters.services.embedding_service.requests.post')
    def test_get_embeddings_no_embedding(self, mock_post):
        print("Test per controllare se viene generato correttamente un embedding per una query quando la risposta HTTP non contiene l'embedding")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        service = EmbeddingService()
        prompt = "test prompt"

        with self.assertRaises(ValueError) as context:
            service.get_embeddings(prompt)

        self.assertEqual(str(context.exception), "Failed to generate embedding for the query.")
        mock_post.assert_called_once_with(OLLAMA_EMBED_URL, json={"model": "nomic-embed-text", "prompt": prompt})

    @patch('app.adapters.services.embedding_service.requests.post')
    def test_get_embeddings_failure(self, mock_post):
        print("Test per controllare se viene generato correttamente un errore quando la richiesta HTTP fallisce")
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        service = EmbeddingService()
        prompt = "test prompt"

        with self.assertRaises(Exception) as context:
            service.get_embeddings(prompt)

        self.assertEqual(str(context.exception), "Failed to get embedding: 500 - Internal Server Error")
        mock_post.assert_called_once_with(OLLAMA_EMBED_URL, json={"model": "nomic-embed-text", "prompt": prompt})

if __name__ == '__main__':
    unittest.main()