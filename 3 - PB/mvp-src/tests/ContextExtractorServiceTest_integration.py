import unittest
from unittest.mock import patch
from App.Adapters.Services.ContextExtractorService import ContextExtractorService

class TestContextExtractorServiceIntegration(unittest.TestCase):

    def setUp(self):
        """Inizializza il servizio prima di ogni test."""
        self.service = ContextExtractorService()

    @patch('App.Adapters.Services.ContextExtractorService.ContextExtractorService.getEmbedding')
    def testProcessUserInput(self, mockGetEmbedding):
        mockGetEmbedding.return_value = [0.1, 0.2, 0.3]
        userInput = "Questo è un esempio di input utente."
        textsToEmbed, etimToEmbed = self.service.processUserInput(userInput)
        self.assertIsInstance(textsToEmbed, list)
        self.assertIsInstance(etimToEmbed, dict)
        print(f"Texts to embed: {textsToEmbed}")
        print(f"Etim to embed: {etimToEmbed}")

    # def testGetEmbedding(self):
    #     """
    #     Testa il metodo getEmbedding con un prompt valido.
    #     """
    #     print("Test per il metodo getEmbedding con un prompt valido.")
    #     prompt = "Questo è un esempio di prompt."
    #     try:
    #         embedding = self.service.getEmbedding(prompt)
    #         self.assertIsInstance(embedding, list)
    #         self.assertGreater(len(embedding), 0)
    #         self.assertTrue(all(isinstance(x, float) for x in embedding))
    #         print(f"Embedding ricevuto: {embedding}")
    #     except Exception as e:
    #         self.fail(f"Errore durante il test: {e}")

    def testGetStructuredProducts(self):
        """
        Testa il metodo getStructuredProducts per verificare che restituisca i prodotti strutturati.
        """
        print("Test per il metodo getStructuredProducts.")
        try:
            structuredProducts = self.service.getStructuredProducts()
            self.assertIsInstance(structuredProducts, list)
            self.assertEqual(len(structuredProducts), 3)  # idList, idTitleList, idTitleDescList
            print(f"Prodotti strutturati: {structuredProducts}")
        except Exception as e:
            self.fail(f"Errore durante il test: {e}")

    @patch('App.Adapters.Services.ContextExtractorService.ContextExtractorService.loadChunks')
    def testLoadChunks(self, mockLoadChunks):
        mockLoadChunks.return_value = [
            {"id": 1, "filename": "file1", "chunk": "chunk1", "embedding": [0.1, 0.2, 0.3]},
            {"id": 2, "filename": "file2", "chunk": "chunk2", "embedding": [0.4, 0.5, 0.6]},
        ]
        chunks = self.service.loadChunks()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        print(f"Chunks caricati: {chunks}")

    def tearDown(self):
        """Chiude la connessione al database dopo ogni test."""
        del self.service

if __name__ == '__main__':
    unittest.main()