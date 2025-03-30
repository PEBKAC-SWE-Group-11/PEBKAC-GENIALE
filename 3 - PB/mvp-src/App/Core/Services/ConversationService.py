import uuid
import uuid
from App.Adapters.Repositories.DBRepository import DBRepository
from App.Core.Entities.Entities import Session, Conversation, Message
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.repository = DBRepository()

    def createSession(self):
        sessionId = str(uuid.uuid4())
        logger.info(f"SESSION: {sessionId}")
        query = "INSERT INTO Session (sessionId, createdAt, updatedAt, isActive) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)"
        self.repository.executeQuery(query, (sessionId,))
        return sessionId

    def readSession(self, sessionId):
        query = "SELECT * FROM Session WHERE sessionId = %s"
        return self.repository.fetchOne(query, (sessionId,))

    def updateSession(self, sessionId):
        """Aggiorna il timestamp updatedAt di una sessione per mantenerla attiva"""
        query = "UPDATE Session SET updatedAt = CURRENT_TIMESTAMP WHERE sessionId = %s"
        self.repository.executeQuery(query, (sessionId,))
        return True

    def createConversation(self, sessionId):
        try:
            query = "INSERT INTO Conversation (sessionId, createdAt, updatedAt, toDelete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversationId"
            return self.repository.fetchOne(query, (sessionId,))[0]
        except Exception as e:
            logging.error(f"Errore creazione conversazione per sessionId={sessionId}: {str(e)}")
            raise

    def readConversations(self, sessionId):
        try:
            query = """
                SELECT * FROM Conversation 
                WHERE sessionId = %s AND (toDelete = FALSE OR toDelete IS NULL) 
                ORDER BY updatedAt DESC
            """
            results = self.repository.fetchAll(query, (sessionId,))
            
            formattedConversations = []
            for row in results:
                if isinstance(row, dict):
                    formattedConversations.append(row)
                else:
                    formattedConv = {
                        'conversationId': row[0],
                        'sessionId': row[1],
                        'createdAt': row[2],
                        'updatedAt': row[3],
                        'toDelete': row[4] if len(row) > 4 else False
                    }
                    formattedConversations.append(formattedConv)
            
            return formattedConversations
        except Exception as e:
            logging.error(f"Errore recupero conversazioni per sessionId={sessionId}: {str(e)}")
            raise

    def readConversationById(self, conversationId):
        query = "SELECT * FROM Conversation WHERE conversationId = %s"
        return self.repository.fetchOne(query, (conversationId,))

    def deleteConversation(self, conversationId):
        query = "UPDATE Conversation SET toDelete = TRUE WHERE conversationId = %s"
        self.repository.executeQuery(query, (conversationId,))

    def updateConversationTimestamp(self, conversationId):
        """Aggiorna il timestamp updatedAt di una conversazione quando l'utente invia un messaggio"""
        query = "UPDATE Conversation SET updatedAt = CURRENT_TIMESTAMP WHERE conversationId = %s"
        self.repository.executeQuery(query, (conversationId,))
        return True

    def addMessage(self, conversationId, sender, content):
        query = "INSERT INTO Message (conversationId, sender, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING messageId"
        messageId = self.repository.fetchOne(query, (conversationId, sender, content))[0]
        
        return messageId

    def readMessages(self, conversationId):
        try:
            query = """
                SELECT m.*, 
                      f.feedbackId,
                      f.isHelpful,
                      f.content as feedbackContent,
                      f.createdAt as feedbackCreatedAt
                FROM Message m 
                LEFT JOIN Feedback f ON m.messageId = f.messageId
                WHERE m.conversationId = %s 
                ORDER BY m.createdAt ASC
            """
            results = self.repository.fetchAll(query, (conversationId,))
            
            formattedMessages = []
            for row in results:
                feedback = None
                if len(row) > 5 and row[5] is not None:
                    feedback = {
                        'feedbackId': str(row[5]),
                        'messageId': str(row[0]),
                        'type': 'positive' if row[6] else 'negative',
                        'content': row[7],
                        'createdAt': str(row[8]) if row[8] else None
                    }
                
                formattedMsg = {
                    'messageId': str(row[0]),
                    'conversationId': str(row[1]),
                    'sender': row[2],
                    'content': row[3],
                    'createdAt': str(row[4]),
                    'feedback': feedback
                }
                formattedMessages.append(formattedMsg)
            
            return formattedMessages
        except Exception as e:
            logging.error(f"Errore recupero messaggi per conversationId={conversationId}: {str(e)}")
            return []
    
    def readFeedback(self, messageId):
        query = "SELECT * FROM Feedback WHERE messageId = %s"
        results = self.repository.fetchAll(query, (messageId,))
        
        formattedFeedback = []
        for row in results:
            feedback = {
                'feedbackId': str(row[0]),
                'messageId': str(row[1]),
                'type': 'positive' if row[2] else 'negative',
                'content': row[3],
                'createdAt': str(row[4]) if len(row) > 4 and row[4] else None
            }
            formattedFeedback.append(feedback)
        
        return formattedFeedback
    
    def addFeedback(self, messageId, feedback, content=None):
        checkQuery = "SELECT COUNT(*) FROM Feedback WHERE messageId = %s"
        count = self.repository.fetchOne(checkQuery, (messageId,))[0]
        
        if count > 0:
            if content:
                query = "UPDATE Feedback SET isHelpful = %s, content = %s WHERE messageId = %s"
                self.repository.executeQuery(query, (feedback == 1, content, messageId))
            else:
                query = "UPDATE Feedback SET isHelpful = %s WHERE messageId = %s"
                self.repository.executeQuery(query, (feedback == 1, messageId))
        else:
            if content:
                query = "INSERT INTO Feedback (messageId, isHelpful, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
                self.repository.executeQuery(query, (messageId, feedback == 1, content))
            else:
                query = "INSERT INTO Feedback (messageId, isHelpful, createdAt) VALUES (%s, %s, CURRENT_TIMESTAMP)"
                self.repository.executeQuery(query, (messageId, feedback == 1))
    
    def readNumPositiveFeedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE isHelpful = TRUE"
        result = self.repository.fetchOne(query)
        return result[0] if result else 0
    
    def readNumNegativeFeedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE isHelpful = FALSE"
        result = self.repository.fetchOne(query)
        return result[0] if result else 0
    
    def readNumConversations(self):
        query = "SELECT COUNT(*) FROM Conversation"
        result = self.repository.fetchOne(query)
        return result[0] if result else 0
        
    def readFeedbackWithComments(self):
        """Recupera i feedback che hanno un commento (content non null)"""
        query = """
            SELECT f.feedbackId, f.messageId, f.isHelpful, f.content, f.createdAt, m.content as messageContent 
            FROM Feedback f
            JOIN Message m ON f.messageId = m.messageId
            WHERE f.content IS NOT NULL AND f.content != ''
            ORDER BY f.createdAt DESC
            LIMIT 50
        """
        results = self.repository.fetchAll(query)
        
        formattedFeedback = []
        for row in results:
            feedback = {
                'feedbackId': str(row[0]),
                'messageId': str(row[1]),
                'type': 'positive' if row[2] else 'negative',
                'content': row[3],
                'createdAt': str(row[4]),
                'messageContent': row[5][:100] + ('...' if len(row[5]) > 100 else '')  # Abbrevia il messaggio originale
            }
            formattedFeedback.append(feedback)
        
        return formattedFeedback