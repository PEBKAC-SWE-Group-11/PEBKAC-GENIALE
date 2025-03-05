from abc import ABC, abstractmethod

class RepositoryPort(ABC):
    @abstractmethod
    def execute_query(self, query, params=None):
        pass

    @abstractmethod
    def fetch_one(self, query, params=None):
        pass

    @abstractmethod
    def fetch_all(self, query, params=None):
        pass

    @abstractmethod
    def close(self):
        pass