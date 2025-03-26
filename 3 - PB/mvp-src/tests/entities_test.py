import sys
import os
import unittest
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.entities.entities import Session, Conversation, Message

class TestEntities(unittest.TestCase):

    def test_session_creation(self):
        print("Test per controllare se una sessione viene creata correttamente senza specificare la data di creazione")
        sessionId = '123'
        session = Session(sessionId)
        self.assertEqual(session.sessionId, sessionId)
        self.assertIsInstance(session.createdAt, datetime)

    def test_session_creation_with_createdAt(self):
        print("Test per controllare se una sessione viene creata correttamente specificando la data di creazione")
        sessionId = '123'
        createdAt = datetime(2025, 3, 10)
        session = Session(sessionId, createdAt)
        self.assertEqual(session.sessionId, sessionId)
        self.assertEqual(session.createdAt, createdAt)

    def test_conversation_creation(self):
        print("Test per controllare se una conversazione viene creata correttamente")
        conversationId = '456'
        sessionId = '123'
        createdAt = '2025-03-10'
        conversation = Conversation(conversationId, sessionId, createdAt)
        self.assertEqual(conversation.conversationId, conversationId)
        self.assertEqual(conversation.sessionId, sessionId)
        self.assertEqual(conversation.createdAt, createdAt)

    def test_message_creation(self):
        print("Test per controllare se un messaggio viene creato correttamente")
        messageId = '789'
        conversationId = '456'
        sender = 'user'
        content = 'Hello'
        createdAt = '2025-03-10'
        message = Message(messageId, conversationId, sender, content, createdAt)
        self.assertEqual(message.messageId, messageId)
        self.assertEqual(message.conversationId, conversationId)
        self.assertEqual(message.sender, sender)
        self.assertEqual(message.content, content)
        self.assertEqual(message.createdAt, createdAt)

if __name__ == '__main__':
    unittest.main()