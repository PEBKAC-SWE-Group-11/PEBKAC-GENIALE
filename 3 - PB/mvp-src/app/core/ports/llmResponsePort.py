from abc import ABC, abstractmethod

class llmResponsePort(ABC):
    @abstractmethod
    def getLlmResponse(self, conversationPile, question, textsToEmbed, etimToEmbed):
        pass
