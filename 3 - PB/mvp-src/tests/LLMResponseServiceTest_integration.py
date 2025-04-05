import unittest
from App.Adapters.Services.LLMResponseService import LLMResponseService

class TestLLMResponseServiceIntegration(unittest.TestCase):

    def setUp(self):
        """Inizializza il servizio prima di ogni test."""
        self.service = LLMResponseService(modelName='llama3.1:8b')

    def testGetLlmResponseValidInput(self):
        """
        Testa il metodo getLlmResponse con input validi.
        """
        print("Test per il metodo getLlmResponse con input validi.")
        conversationPile = [
            {"sender": "user", "content": "Ciao, come stai?"},
            {"sender": "assistant", "content": "Sto bene, grazie! Come posso aiutarti?"}
        ]
        question = "Qual è la capitale della Francia?"
        textsToEmbed = [
            [1, "file1", "chunk1", "Parigi è la capitale della Francia."],
            [2, "file2", "chunk2", "La Francia è un paese in Europa."]
        ]
        etimToEmbed = {
            "1": {"title": "Geografia", "description": "Informazioni sulla Francia"},
            "2": {"title": "Storia", "description": "Storia della Francia"}
        }

        try:
            response = self.service.getLlmResponse(conversationPile, question, textsToEmbed, etimToEmbed)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            print(f"Risposta ricevuta: {response}")
        except Exception as e:
            self.fail(f"Errore durante il test: {e}")

    def testGetLlmResponseEmptyContext(self):
        """
        Testa il metodo getLlmResponse con un contesto vuoto.
        """
        print("Test per il metodo getLlmResponse con un contesto vuoto.")
        conversationPile = [
            {"sender": "user", "content": "Ciao, come stai?"},
            {"sender": "assistant", "content": "Sto bene, grazie! Come posso aiutarti?"}
        ]
        question = "Qual è la capitale della Francia?"
        textsToEmbed = []
        etimToEmbed = {}

        try:
            response = self.service.getLlmResponse(conversationPile, question, textsToEmbed, etimToEmbed)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            print(f"Risposta ricevuta: {response}")
        except Exception as e:
            self.fail(f"Errore durante il test: {e}")

    def testGetLlmResponseInvalidModel(self):
        """
        Testa il metodo getLlmResponse con un modello non valido.
        """
        print("Test per il metodo getLlmResponse con un modello non valido.")
        invalidService = LLMResponseService(modelName='invalid-model')
        conversationPile = [
            {"sender": "user", "content": "Ciao, come stai?"},
            {"sender": "assistant", "content": "Sto bene, grazie! Come posso aiutarti?"}
        ]
        question = "Qual è la capitale della Francia?"
        textsToEmbed = [
            [1, "file1", "chunk1", "Parigi è la capitale della Francia."]
        ]
        etimToEmbed = {
            "1": {"title": "Geografia", "description": "Informazioni sulla Francia"}
        }

        try:
            response = invalidService.getLlmResponse(conversationPile, question, textsToEmbed, etimToEmbed)
            self.assertEqual(response, "Failed to get response")
            print("Risposta fallita gestita correttamente.")
        except Exception as e:
            self.fail(f"Errore durante il test: {e}")

if __name__ == '__main__':
    unittest.main()