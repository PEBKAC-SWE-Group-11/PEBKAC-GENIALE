from abc import ABC, abstractmethod

class ContextExtractorPort(ABC):
    @abstractmethod
    def processUserInput(self, userInput):
        pass

    @abstractmethod
    def _getStructuredProducts(self):
        pass

    @abstractmethod
    def _loadChunks(self):
        pass

    @abstractmethod
    def _extractEtim(self):
        pass

    @abstractmethod
    def _getEmbedding(self, prompt):
        pass

    @abstractmethod
    def _selectChunksEmbeddings(self, chunksEmbeddings, processedSimilarProducts):
        pass
