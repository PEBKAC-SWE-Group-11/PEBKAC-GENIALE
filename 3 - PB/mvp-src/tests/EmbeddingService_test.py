import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from App.Adapters.Services.ContextExtractorService import ContextExtractorService, EMBEDDING_MODEL

class TestEmbeddingService(unittest.TestCase):

    @patch('App.Adapters.Services.ContextExtractorService.ollama.embeddings')
    def testGetEmbeddingsSuccess(self, mockEmbeddings):
        print("Test per controllare se viene generato correttamente un embedding per una query quando la richiesta ha successo")
        mockEmbeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        service = ContextExtractorService()
        prompt = "test prompt"
        result = service.getEmbedding(prompt)

        self.assertEqual(result, [0.1, 0.2, 0.3])
        mockEmbeddings.assert_called_once_with(model=EMBEDDING_MODEL, prompt=prompt)

    @patch('App.Adapters.Services.ContextExtractorService.ollama.embeddings')
    def testGetEmbeddingsNoEmbedding(self, mockEmbeddings):
        print("Test per controllare se viene generato correttamente un errore quando la risposta non contiene l'embedding")
        mockEmbeddings.return_value = {}

        service = ContextExtractorService()
        prompt = "test prompt"

        with self.assertRaises(ValueError) as context:
            service.getEmbedding(prompt)

        self.assertEqual(str(context.exception), "Failed to generate embedding for the query.")
        mockEmbeddings.assert_called_once_with(model=EMBEDDING_MODEL, prompt=prompt)

    @patch('App.Adapters.Services.ContextExtractorService.ollama.embeddings')
    def testGetEmbeddingsFailure(self, mockEmbeddings):
        print("Test per controllare se viene generato correttamente un errore quando la richiesta fallisce")
        mockEmbeddings.side_effect = Exception("Internal Server Error")

        service = ContextExtractorService()
        prompt = "test prompt"

        with self.assertRaises(ValueError) as context:
            service.getEmbedding(prompt)

        self.assertEqual(str(context.exception), "Failed to generate embedding for the query.")
        mockEmbeddings.assert_called_once_with(model=EMBEDDING_MODEL, prompt=prompt)

if __name__ == '__main__':
    unittest.main()