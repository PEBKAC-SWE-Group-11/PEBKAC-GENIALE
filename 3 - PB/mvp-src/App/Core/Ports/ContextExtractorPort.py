from abc import ABC, abstractmethod

class ContextExtractorPort(ABC):
    @abstractmethod
    def processUserInput(self, userInput):
        pass

    @abstractmethod
    def getStructuredProducts(self):
        pass

    @abstractmethod
    def loadChunks(self):
        pass

    @abstractmethod
    def extractEtim(self):
        pass

    @abstractmethod
    def getEmbedding(self, prompt):
        pass

    @abstractmethod
    def selectChunksEmbeddings(self, chunksEmbeddings, processedSimilarProducts):
        pass
