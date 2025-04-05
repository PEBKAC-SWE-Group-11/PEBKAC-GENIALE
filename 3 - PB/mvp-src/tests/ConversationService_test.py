import os
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Core.Services.ConversationService import ConversationService

class TestConversationService(unittest.TestCase):

    @patch('App.Core.Services.ConversationService.DBRepository')
    def setUp(self, MockDbRepository):
        self.mockRepository = MockDbRepository.return_value
        self.service = ConversationService()

    def testCreateSession(self):
        print("Test per inserire correttamente una nuova sessione nel database")
        sessionId = '123'
        self.service.createSession()
        query = "INSERT INTO Session (sessionId, createdAt, updatedAt, isActive) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)"
        self.mockRepository.executeQuery.assert_called_once_with(query, (unittest.mock.ANY,))

    def testReadSession(self):
        print("Test per controllare se viene recuperata correttamente una sessione dal database")
        sessionId = '123'
        self.mockRepository.fetchOne.return_value = ('123', True)  # Mock corretto
        result = self.service.readSession(sessionId)
        query = "SELECT sessionId, isActive FROM Session WHERE sessionId = %s"  # Query aggiornata
        self.mockRepository.fetchOne.assert_called_once_with(query, (sessionId,))
        self.assertEqual(result, {
            'sessionId': '123',
            'isActive': True
        })

    def testCreateConversation(self):
        print("Test per controllare se viene creata correttamente una nuova conversazione nel database")
        sessionId = '123'
        self.mockRepository.fetchOne.return_value = ('456',)
        result = self.service.createConversation(sessionId)
        query = "INSERT INTO Conversation (sessionId, createdAt, updatedAt, toDelete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversationId"
        self.mockRepository.fetchOne.assert_called_once_with(query, (sessionId,))
        self.assertEqual(result, '456')

    def testReadConversations(self):
        print("Test per controllare se vengono recuperate correttamente tutte le conversazioni associate a una sessione dal database")
        sessionId = '123'
        self.mockRepository.fetchAll.return_value = [
            ('456', '123', '2025-03-10', '2025-03-11', False)
        ]
        result = self.service.readConversations(sessionId)
        query = """SELECT * FROM Conversation WHERE sessionId = %s AND (toDelete = FALSE OR toDelete IS NULL) ORDER BY updatedAt DESC"""
        self.mockRepository.fetchAll.assert_called_once_with(query.strip(), (sessionId,))
        self.assertEqual(result, [{
            'conversationId': '456',
            'sessionId': '123',
            'createdAt': '2025-03-10',
            'updatedAt': '2025-03-11',
            'toDelete': False
        }])

    def testDeleteConversation(self):
        print("Test per controllare se viene eliminata correttamente una conversazione dal database")
        conversationId = '456'
        self.service.deleteConversation(conversationId)
        query = "UPDATE Conversation SET toDelete = TRUE WHERE conversationId = %s"
        self.mockRepository.executeQuery.assert_called_once_with(query, (conversationId,))

    def testAddMessage(self):
        print("Test per controllare se viene aggiunto correttamente un nuovo messaggio a una conversazione nel database")
        conversationId = '456'
        sender = 'user'
        content = 'Hello'
        self.mockRepository.fetchOne.return_value = ('789', '2025-03-10 12:00:00')  # Mock corretto
        result = self.service.addMessage(conversationId, sender, content)
        query = "INSERT INTO Message (conversationId, sender, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING messageId, createdAt"
        self.mockRepository.fetchOne.assert_called_once_with(query, (conversationId, sender, content))
        self.assertEqual(result, '789')

    def testReadMessages(self):
        print("Test per controllare se vengono recuperati correttamente tutti i messaggi associati a una conversazione dal database")
        conversationId = '456'
        self.mockRepository.fetchAll.return_value = [('789', '456', 'user', 'Hello', '2025-03-10', None, None, None, None)]
        result = self.service.readMessages(conversationId)
        query = """SELECT m.*, f.feedbackId, f.isHelpful,f.content as feedbackContent, f.createdAt as feedbackCreatedAt FROM Message m LEFT JOIN Feedback f ON m.messageId = f.messageId WHERE m.conversationId = %s ORDER BY m.createdAt ASC"""
        self.mockRepository.fetchAll.assert_called_once_with(query.strip(), (conversationId,))
        self.assertEqual(result, [{
            'messageId': '789',
            'conversationId': '456',
            'sender': 'user',
            'content': 'Hello',
            'createdAt': '2025-03-10',
            'feedback': None
        }])

if __name__ == '__main__':
    unittest.main()


