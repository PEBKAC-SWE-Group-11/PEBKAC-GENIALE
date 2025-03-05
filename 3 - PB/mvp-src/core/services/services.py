from ..repositories.repositories import SessionRepository, ConversationRepository, MessageRepository, VectorDatabaseRepository, ProductRepository
from ..entities.entities import Session, Conversation, Message
from typing import List, Dict
import logging
import ollama
import requests
import psycopg2


class SessionService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def create_session(self, session_id: str) -> str:
        return self.repository.create_session(session_id)

    def get_session(self, session_id: str) -> Session:
        return self.repository.read_session(session_id)


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create_conversation(self, session_id: str) -> str:
        return self.repository.create_conversation(session_id)

    def get_conversations(self, session_id: str) -> list[Conversation]:
        return self.repository.read_conversations(session_id)

    def get_conversation_by_id(self, conversation_id: str) -> Conversation:
        return self.repository.read_conversation_by_id(conversation_id)

    def delete_conversation(self, conversation_id: str) -> None:
        self.repository.delete_conversation(conversation_id)


class MessageService:
    def __init__(self, repository: MessageRepository):
        self.repository = repository

    def add_message(self, conversation_id: str, sender: str, content: str) -> str:
        return self.repository.add_message(conversation_id, sender, content)

    def get_messages(self, conversation_id: str) -> list[Message]:
        return self.repository.read_messages(conversation_id)


class AIModelService:
    def __init__(self, model_name: str = 'llama3.2:1b'):
        self.model_name = model_name

    def get_llm_response(self, messages: List[Dict], question: str, text_to_embed: str) -> str:
        # Logica per interagire con il modello AI
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["sender"],
                "content": msg["content"]
            })

        system_context = f"Usa questo contesto per rispondere: {text_to_embed}"
        formatted_messages.extend([
            {"role": "system", "content": system_context},
            {"role": "user", "content": question}
        ])

        logging.info(f"Sending messages to AI model: {formatted_messages}")

        try:
            stream = ollama.chat(
                model=self.model_name,
                messages=formatted_messages,
                stream=True
            )

            response = ""
            for chunk in stream:
                if chunk and "message" in chunk and "content" in chunk["message"]:
                    response += chunk["message"]["content"]

            logging.info(f"Raw response from AI model: {response}")

            if response.startswith("Assistant: "):
                response = response[11:]

            logging.info(f"Cleaned response: {response}")
            return response

        except Exception as e:
            logging.error(f"Error with AI model API: {e}", exc_info=True)
            return "Mi dispiace, si è verificato un errore nella generazione della risposta."


class EmbeddingService:
    def __init__(self, repository: VectorDatabaseRepository, embed_url: str = "http://localhost:11434/api/embeddings"):
        self.repository = repository
        self.embed_url = embed_url

    def get_embeddings(self, prompt: str):
        payload = {
            "model": "nomic-embed-text",
            "prompt": f"{prompt}"
        }

        response = requests.post(self.embed_url, json=payload)

        if response.status_code == 200:
            query_vector = response.json().get("embedding")
            if not query_vector:
                raise ValueError("Failed to generate embedding for the query.")
        else:
            raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

        return self.repository.search_similar_products(query_vector)


class DataInsertionService:
    def __init__(self, product_repository: ProductRepository, embed_url: str = "http://localhost:11434/api/embeddings"):
        self.product_repository = product_repository
        self.embed_url = embed_url

    def insert_data(self, data, chunk_data):
        connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )
        cursor = connection.cursor()

        try:
            for product in data['vimar_datas']:
                print(f"Inserting product {product['id']}...")
                self.product_repository.insert_product(cursor, product)
                connection.commit()

            for chunk in chunk_data['chunks']:
                print(f"Inserting chunk for product {chunk['id']}...")
                self.product_repository.insert_chunk(cursor, chunk)
                connection.commit()

        except Exception as e:
            logging.error(f"Error inserting products: {e}")
        finally:
            if cursor:
                print("Committing changes...")
                cursor.close()
            if connection:
                connection.close()


# Test per la classe SessionService
import unittest
from unittest.mock import MagicMock
from ..repositories.repositories import SessionRepository
from ..entities.entities import Session

class TestSessionService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=SessionRepository)
        self.service = SessionService(self.mock_repository)

    def test_create_session(self):
        session_id = '123'
        self.mock_repository.create_session.return_value = session_id
        result = self.service.create_session(session_id)
        self.assertEqual(result, session_id)
        self.mock_repository.create_session.assert_called_once_with(session_id)

    def test_get_session(self):
        session_id = '123'
        session = Session(session_id, '2023-10-01')
        self.mock_repository.read_session.return_value = session
        result = self.service.get_session(session_id)
        self.assertEqual(result, session)
        self.mock_repository.read_session.assert_called_once_with(session_id)


# Test per la classe ConversationService
class TestConversationService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=ConversationRepository)
        self.service = ConversationService(self.mock_repository)

    def test_create_conversation(self):
        session_id = '123'
        conversation_id = '456'
        self.mock_repository.create_conversation.return_value = conversation_id
        result = self.service.create_conversation(session_id)
        self.assertEqual(result, conversation_id)
        self.mock_repository.create_conversation.assert_called_once_with(session_id)

    def test_get_conversations(self):
        session_id = '123'
        conversations = [Conversation('456', session_id, '2023-10-01')]
        self.mock_repository.read_conversations.return_value = conversations
        result = self.service.get_conversations(session_id)
        self.assertEqual(result, conversations)
        self.mock_repository.read_conversations.assert_called_once_with(session_id)


# Test per la classe MessageService
class TestMessageService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=MessageRepository)
        self.service = MessageService(self.mock_repository)

    def test_add_message(self):
        conversation_id = '456'
        sender = 'user'
        content = 'Hello'
        message_id = '789'
        self.mock_repository.add_message.return_value = message_id
        result = self.service.add_message(conversation_id, sender, content)
        self.assertEqual(result, message_id)
        self.mock_repository.add_message.assert_called_once_with(conversation_id, sender, content)

    def test_get_messages(self):
        conversation_id = '456'
        messages = [Message('789', conversation_id, 'user', 'Hello', '2023-10-01')]
        self.mock_repository.read_messages.return_value = messages
        result = self.service.get_messages(conversation_id)
        self.assertEqual(result, messages)
        self.mock_repository.read_messages.assert_called_once_with(conversation_id)


if __name__ == '__main__':
    unittest.main() 