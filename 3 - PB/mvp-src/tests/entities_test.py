import sys
import os
import unittest
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.entities.entities import Session, Conversation, Message

class TestEntities(unittest.TestCase):

    def test_session_creation(self):
        print("Test per controllare se una sessione viene creata correttamente senza specificare la data di creazione")
        session_id = '123'
        session = Session(session_id)
        self.assertEqual(session.session_id, session_id)
        self.assertIsInstance(session.created_at, datetime)

    def test_session_creation_with_created_at(self):
        print("Test per controllare se una sessione viene creata correttamente specificando la data di creazione")
        session_id = '123'
        created_at = datetime(2025, 3, 10)
        session = Session(session_id, created_at)
        self.assertEqual(session.session_id, session_id)
        self.assertEqual(session.created_at, created_at)

    def test_conversation_creation(self):
        print("Test per controllare se una conversazione viene creata correttamente")
        conversation_id = '456'
        session_id = '123'
        created_at = '2025-03-10'
        conversation = Conversation(conversation_id, session_id, created_at)
        self.assertEqual(conversation.conversation_id, conversation_id)
        self.assertEqual(conversation.session_id, session_id)
        self.assertEqual(conversation.created_at, created_at)

    def test_message_creation(self):
        print("Test per controllare se un messaggio viene creato correttamente")
        message_id = '789'
        conversation_id = '456'
        sender = 'user'
        content = 'Hello'
        created_at = '2025-03-10'
        message = Message(message_id, conversation_id, sender, content, created_at)
        self.assertEqual(message.message_id, message_id)
        self.assertEqual(message.conversation_id, conversation_id)
        self.assertEqual(message.sender, sender)
        self.assertEqual(message.content, content)
        self.assertEqual(message.created_at, created_at)

if __name__ == '__main__':
    unittest.main()