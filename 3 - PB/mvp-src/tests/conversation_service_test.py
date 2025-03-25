import os
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.services.conversation_service import ConversationService

class TestConversationService(unittest.TestCase):

    @patch('app.core.services.conversation_service.DBRepository')
    def setUp(self, MockDBRepository):
        self.mock_repository = MockDBRepository.return_value
        self.service = ConversationService()

    def test_create_session(self):
        print("Test per inserire correttamente una nuova sessione nel database")
        session_id = '123'
        self.service.create_session()
        query = "INSERT INTO Session (session_id, created_at, updated_at, is_active) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)"
        self.mock_repository.execute_query.assert_called_once_with(query, (unittest.mock.ANY,))

    def test_read_session(self):
        print("Test per controllare se viene recuperata correttamente una sessione dal database")
        session_id = '123'
        self.mock_repository.fetch_one.return_value = ('123', '2025-03-10')
        result = self.service.read_session(session_id)
        query = "SELECT * FROM Session WHERE session_id = %s"
        self.mock_repository.fetch_one.assert_called_once_with(query, (session_id,))
        self.assertEqual(result, ('123', '2025-03-10'))

    def test_create_conversation(self):
        print("Test per controllare se viene creata correttamente una nuova conversazione nel database")
        session_id = '123'
        self.mock_repository.fetch_one.return_value = ('456',)
        result = self.service.create_conversation(session_id)
        query = "INSERT INTO Conversation (session_id, created_at, updated_at, to_delete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversation_id"
        self.mock_repository.fetch_one.assert_called_once_with(query, (session_id,))
        self.assertEqual(result, '456')

    def test_read_conversations(self):
        print("Test per controllare se vengono recuperate correttamente tutte le conversazioni associate a una sessione dal database")
        session_id = '123'
        self.mock_repository.fetch_all.return_value = [
            ('456', '123', '2025-03-10', '2025-03-11', False)
        ]
        result = self.service.read_conversations(session_id)
        query = """SELECT * FROM Conversation WHERE session_id = %s AND (to_delete = FALSE OR to_delete IS NULL) ORDER BY updated_at DESC"""
        self.mock_repository.fetch_all.assert_called_once_with(query.strip(), (session_id,))
        self.assertEqual(result, [{
            'conversation_id': '456',
            'session_id': '123',
            'created_at': '2025-03-10',
            'updated_at': '2025-03-11',
            'to_delete': False
        }])

    def test_read_conversation_by_id(self):
        print("Test per controllare se viene recuperata correttamente una conversazione dal database tramite il suo id della conversazione")
        conversation_id = '456'
        self.mock_repository.fetch_one.return_value = ('456', '123', '2025-03-10')
        result = self.service.read_conversation_by_id(conversation_id)
        query = "SELECT * FROM Conversation WHERE conversation_id = %s"
        self.mock_repository.fetch_one.assert_called_once_with(query, (conversation_id,))
        self.assertEqual(result, ('456', '123', '2025-03-10'))

    def test_delete_conversation(self):
        print("Test per controllare se viene eliminata correttamente una conversazione dal database")
        conversation_id = '456'
        self.service.delete_conversation(conversation_id)
        query = "UPDATE Conversation SET to_delete = TRUE WHERE conversation_id = %s"
        self.mock_repository.execute_query.assert_called_once_with(query, (conversation_id,))

    def test_add_message(self):
        print("Test per controllare se viene aggiunto correttamente un nuovo messaggio a una conversazione nel database")
        conversation_id = '456'
        sender = 'user'
        content = 'Hello'
        self.mock_repository.fetch_one.return_value = ('789',)
        result = self.service.add_message(conversation_id, sender, content)
        query = "INSERT INTO Message (conversation_id, sender, content, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING message_id"
        self.mock_repository.fetch_one.assert_called_once_with(query, (conversation_id, sender, content))
        self.assertEqual(result, '789')

    def test_read_messages(self):
        print("Test per controllare se vengono recuperati correttamente tutti i messaggi associati a una conversazione dal database")
        conversation_id = '456'
        self.mock_repository.fetch_all.return_value = [('789', '456', 'user', 'Hello', '2025-03-10', None, None, None, None)]
        result = self.service.read_messages(conversation_id)
        query = """SELECT m.*, f.feedback_id, f.is_helpful, f.content as feedback_content, f.created_at as feedback_created_at FROM Message m LEFT JOIN Feedback f ON m.message_id = f.message_id WHERE m.conversation_id = %s ORDER BY m.created_at ASC"""
        self.mock_repository.fetch_all.assert_called_once_with(query.strip(), (conversation_id,))
        self.assertEqual(result, [{
            'message_id': '789',
            'conversation_id': '456',
            'sender': 'user',
            'content': 'Hello',
            'created_at': '2025-03-10',
            'feedback': None
        }])

    def test_read_feedback(self):
        print("Test per controllare se vengono recuperati correttamente tutti i feedback associati a un messaggio dal database")
        message_id = '789'
        self.mock_repository.fetch_all.return_value = [('789', 'positive', '2025-03-10')]
        result = self.service.read_feedback(message_id)
        query = "SELECT * FROM Feedback WHERE message_id = %s"
        self.mock_repository.fetch_all.assert_called_once_with(query, (message_id,))
        self.assertEqual(result, [('789', 'positive', '2025-03-10')])

    def test_add_feedback(self):
        print("Test per controllare se viene aggiunto correttamente un feedback a un messaggio nel database")
        message_id = '789'
        feedback = 'positive'
        self.mock_repository.fetch_one.return_value = (0,)  # Simula che non ci siano feedback esistenti
        self.service.add_feedback(message_id, feedback)
        query = "INSERT INTO Feedback (message_id, is_helpful, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)"
        self.mock_repository.execute_query.assert_called_once_with(query, (message_id, feedback == 1))

    def test_read_num_positive_feedback(self):
        print("Test per controllare se viene recuperato correttamente il numero di feedback positivi dal database")
        self.mock_repository.fetch_one.return_value = (10,)
        result = self.service.read_num_positive_feedback()
        query = "SELECT COUNT(*) FROM Feedback WHERE is_helpful = TRUE"
        self.mock_repository.fetch_one.assert_called_once_with(query)
        self.assertEqual(result, 10)

    def test_read_num_negative_feedback(self):
        print("Test per controllare se viene recuperato correttamente il numero di feedback negativi dal database")
        self.mock_repository.fetch_one.return_value = (5,)
        result = self.service.read_num_negative_feedback()
        query = "SELECT COUNT(*) FROM Feedback WHERE is_helpful = FALSE"
        self.mock_repository.fetch_one.assert_called_once_with(query)
        self.assertEqual(result, 5)

    def test_read_num_conversations(self):
        print("Test per controllare se viene recuperato correttamente il numero di conversazioni dal database")
        self.mock_repository.fetch_one.return_value = (20,)
        result = self.service.read_num_conversations()
        query = "SELECT COUNT(*) FROM Conversation"
        self.mock_repository.fetch_one.assert_called_once_with(query)
        self.assertEqual(result, 20)

if __name__ == '__main__':
    unittest.main()


