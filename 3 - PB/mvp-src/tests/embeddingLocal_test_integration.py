import unittest
from data_processing.embeddingLocal import getEmbedding

class TestEmbeddingLocalIntegration(unittest.TestCase):

    def test_getEmbedding_valid_input(self):
        """
        Testa il comportamento reale di getEmbedding con un input valido.
        """
        result = getEmbedding("valid input")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(isinstance(x, float) for x in result))

    def test_getEmbedding_empty_input(self):
        """
        Testa il comportamento reale di getEmbedding con un input vuoto.
        """
        result = getEmbedding("")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_getEmbedding_large_input(self):
        """
        Testa il comportamento reale di getEmbedding con un input molto grande.
        """
        large_input = "large input " * 1000
        result = getEmbedding(large_input)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(isinstance(x, float) for x in result))

if __name__ == '__main__':
    unittest.main()