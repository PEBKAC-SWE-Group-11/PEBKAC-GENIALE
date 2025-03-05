from abc import ABC, abstractmethod
from ..entities.entities import Session, Conversation, Message
import psycopg2
import logging


class SessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: str) -> str:
        pass

    @abstractmethod
    def read_session(self, session_id: str) -> Session:
        pass


class ConversationRepository(ABC):
    @abstractmethod
    def create_conversation(self, session_id: str) -> str:
        pass

    @abstractmethod
    def read_conversations(self, session_id: str) -> list[Conversation]:
        pass

    @abstractmethod
    def read_conversation_by_id(self, conversation_id: str) -> Conversation:
        pass

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> None:
        pass


class MessageRepository(ABC):
    @abstractmethod
    def add_message(self, conversation_id: str, sender: str, content: str) -> str:
        pass

    @abstractmethod
    def read_messages(self, conversation_id: str) -> list[Message]:
        pass


class VectorDatabaseRepository(ABC):
    @abstractmethod
    def search_similar_products(self, query_vector, top_k=1):
        pass


class PostgresVectorDatabaseRepository(VectorDatabaseRepository):
    def search_similar_products(self, query_vector, top_k=1):
        try:
            connection = psycopg2.connect(
                database="postgres",
                user="postgres",
                password="pebkac",
                host="db",
                port="5432"
            )
            cursor = connection.cursor()

            query = """
                SELECT id, chunk, embedding <-> %s::vector AS distance
                FROM chunk
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
            """
            cursor.execute(query, (query_vector, query_vector, top_k))
            results = cursor.fetchall()

            for row in results:
                print(f"ID: {row[0]}, Distance: {row[2]}")
                print(f"Text Content: {row[1]}\n")
                return row[0], row[1]

        except Exception as e:
            logging.error(f"Error querying database: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


class ProductRepository(ABC):
    @abstractmethod
    def insert_product(self, cursor, product):
        pass

    @abstractmethod
    def insert_chunk(self, cursor, chunk_product):
        pass


class PostgresProductRepository(ProductRepository):
    def insert_product(self, cursor, product):
        # Logica per inserire un prodotto nel database
        pass

    def insert_chunk(self, cursor, chunk_product):
        # Logica per inserire un chunk nel database
        pass 