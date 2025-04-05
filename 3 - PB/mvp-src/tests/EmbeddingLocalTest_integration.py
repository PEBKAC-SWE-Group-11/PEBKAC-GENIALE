import unittest
from DataProcessing.EmbeddingLocal import getEmbedding

class TestEmbeddingLocalIntegration(unittest.TestCase):

    def testGetEmbeddingValidInput(self):
        """
        Testa il comportamento reale di getEmbedding con un input valido.
        """
        print("Test per la funzione getEmbedding: Verifica che la funzione restituisca un vettore di embedding valido per un input corretto")
        result = getEmbedding("valid input")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(isinstance(x, float) for x in result))

    def testGetEmbeddingEmptyInput(self):
        """
        Testa il comportamento reale di getEmbedding con un input vuoto.
        """
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un input vuoto restituendo un vettore vuoto")
        result = getEmbedding("")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def testGetEmbeddingLargeInput(self):
        """
        Testa il comportamento reale di getEmbedding con un input molto grande.
        """
        print("Test per la funzione getEmbedding: Verifica che la funzione gestisca correttamente un input molto grande restituendo un vettore di embedding valido")
        largeInput = "large input " * 1000
        result = getEmbedding(largeInput)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(isinstance(x, float) for x in result))

if __name__ == '__main__':
    unittest.main()