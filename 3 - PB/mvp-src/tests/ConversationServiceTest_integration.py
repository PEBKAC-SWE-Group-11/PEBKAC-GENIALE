import unittest
from unittest.mock import MagicMock, patch
from App.Core.Services.ConversationService import ConversationService

class TestConversationService(unittest.TestCase):

    def setUp(self):
        """Inizializza il servizio e mocka il repository."""
        self.service = ConversationService()
        self.service.repository = MagicMock()

    def testCreateSession(self):
        """Testa la creazione di una sessione."""
        self.service.repository.executeQuery.return_value = None
        sessionId = self.service.createSession()
        self.assertIsInstance(sessionId, str)
        self.service.repository.executeQuery.assert_called_once()

    def testReadSession(self):
        """Testa la lettura di una sessione."""
        self.service.repository.fetchOne.return_value = ("session-id", True)
        session = self.service.readSession("session-id")
        self.assertEqual(session, {'sessionId': "session-id", 'isActive': True})
        self.service.repository.fetchOne.assert_called_once_with(
            "SELECT sessionId, isActive FROM Session WHERE sessionId = %s", ("session-id",)
        )

    def testUpdateSession(self):
        """Testa l'aggiornamento di una sessione."""
        self.service.repository.executeQuery.return_value = None
        result = self.service.updateSession("session-id")
        self.assertTrue(result)
        self.service.repository.executeQuery.assert_called_once_with(
            "UPDATE Session SET updatedAt = CURRENT_TIMESTAMP WHERE sessionId = %s", ("session-id",)
        )

    def testCreateConversation(self):
        """Testa la creazione di una conversazione."""
        self.service.repository.fetchOne.return_value = ("conversation-id",)
        conversationId = self.service.createConversation("session-id")
        self.assertEqual(conversationId, "conversation-id")
        self.service.repository.fetchOne.assert_called_once_with(
            "INSERT INTO Conversation (sessionId, createdAt, updatedAt, toDelete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversationId",
            ("session-id",)
        )

    def testReadConversations(self):
        """Testa la lettura delle conversazioni."""
        self.service.repository.fetchAll.return_value = [
            (1, "session-id", "2025-04-05 10:00:00", "2025-04-05 10:30:00", False)
        ]
        conversations = self.service.readConversations("session-id")
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]['conversationId'], 1)
        self.service.repository.fetchAll.assert_called_once_with(
            """SELECT * FROM Conversation WHERE sessionId = %s AND (toDelete = FALSE OR toDelete IS NULL) ORDER BY updatedAt DESC""",
            ("session-id",)
        )

    def testAddMessage(self):
        """Testa l'aggiunta di un messaggio."""
        self.service.repository.fetchOne.return_value = ("message-id", "2025-04-05 10:30:00")
        messageId = self.service.addMessage("conversation-id", "user", "Hello!")
        self.assertEqual(messageId, "message-id")
        self.service.repository.fetchOne.assert_called_once_with(
            "INSERT INTO Message (conversationId, sender, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING messageId, createdAt",
            ("conversation-id", "user", "Hello!")
        )
        self.service.repository.executeQuery.assert_called_once_with(
            "UPDATE Conversation SET updatedAt = %s WHERE conversationId = %s",
            ("2025-04-05 10:30:00", "conversation-id")
        )

    def testReadMessages(self):
        """Testa la lettura dei messaggi."""
        self.service.repository.fetchAll.return_value = [
            (1, "conversation-id", "user", "Hello!", "2025-04-05 10:00:00", None, None, None, None)
        ]
        messages = self.service.readMessages("conversation-id")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['messageId'], "1")
        self.service.repository.fetchAll.assert_called_once_with(
            """SELECT m.*, f.feedbackId, f.isHelpful,f.content as feedbackContent, f.createdAt as feedbackCreatedAt FROM Message m LEFT JOIN Feedback f ON m.messageId = f.messageId WHERE m.conversationId = %s ORDER BY m.createdAt ASC""",
            ("conversation-id",)
        )

    def testAddFeedback(self):
        """Testa l'aggiunta di un feedback."""
        self.service.repository.fetchOne.return_value = (0,)
        self.service.addFeedback("message-id", True, "Great message!")
        self.service.repository.fetchOne.assert_called_once_with(
            "SELECT COUNT(*) FROM Feedback WHERE messageId = %s", ("message-id",)
        )
        self.service.repository.executeQuery.assert_called_once_with(
            "INSERT INTO Feedback (messageId, isHelpful, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
            ("message-id", True, "Great message!")
        )

    def testReadNumPositiveFeedback(self):
        """Testa la lettura del numero di feedback positivi."""
        self.service.repository.fetchOne.return_value = (5,)
        numPositive = self.service.readNumPositiveFeedback()
        self.assertEqual(numPositive, 5)
        self.service.repository.fetchOne.assert_called_once_with(
            "SELECT COUNT(*) FROM Feedback WHERE isHelpful = TRUE"
        )

    def testReadNumNegativeFeedback(self):
        """Testa la lettura del numero di feedback negativi."""
        self.service.repository.fetchOne.return_value = (3,)
        numNegative = self.service.readNumNegativeFeedback()
        self.assertEqual(numNegative, 3)
        self.service.repository.fetchOne.assert_called_once_with(
            "SELECT COUNT(*) FROM Feedback WHERE isHelpful = FALSE"
        )

if __name__ == '__main__':
    unittest.main()