from abc import ABC, abstractmethod

class RepositoryPort(ABC):
    @abstractmethod
    def executeQuery(self, query, params=None):
        pass

    @abstractmethod
    def fetchOne(self, query, params=None):
        pass

    @abstractmethod
    def fetchAll(self, query, params=None):
        pass

    @abstractmethod
    def close(self):
        pass