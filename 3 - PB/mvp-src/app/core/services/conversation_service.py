import uuid
import uuid
from app.adapters.repositories.db_repository import DBRepository
from app.core.entities.entities import Session, Conversation, Message
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self):
        self.repository = DBRepository()

    def create_session(self):
        sessionId = str(uuid.uuid4())
        logger.info(f"SESSION: {sessionId}")
        query = "INSERT INTO Session (sessionId, createdAt, updatedAt, isActive) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)"
        self.repository.execute_query(query, (sessionId,))
        return sessionId

    def read_session(self, sessionId):
        query = "SELECT * FROM Session WHERE sessionId = %s"
        return self.repository.fetch_one(query, (sessionId,))

    def update_session(self, sessionId):
        """Aggiorna il timestamp updatedAt di una sessione per mantenerla attiva"""
        query = "UPDATE Session SET updatedAt = CURRENT_TIMESTAMP WHERE sessionId = %s"
        self.repository.execute_query(query, (sessionId,))
        return True

    def create_conversation(self, sessionId):
        try:
            query = "INSERT INTO Conversation (sessionId, createdAt, updatedAt, toDelete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversationId"
            return self.repository.fetch_one(query, (sessionId,))[0]
        except Exception as e:
            logging.error(f"Errore creazione conversazione per sessionId={sessionId}: {str(e)}")
            raise

    def read_conversations(self, sessionId):
        try:
            query = """
                SELECT * FROM Conversation 
                WHERE sessionId = %s AND (toDelete = FALSE OR toDelete IS NULL) 
                ORDER BY updatedAt DESC
            """
            results = self.repository.fetch_all(query, (sessionId,))
            
            formatted_conversations = []
            for row in results:
                if isinstance(row, dict):
                    formatted_conversations.append(row)
                else:
                    formatted_conv = {
                        'conversationId': row[0],
                        'sessionId': row[1],
                        'createdAt': row[2],
                        'updatedAt': row[3],
                        'toDelete': row[4] if len(row) > 4 else False
                    }
                    formatted_conversations.append(formatted_conv)
            
            return formatted_conversations
        except Exception as e:
            logging.error(f"Errore recupero conversazioni per sessionId={sessionId}: {str(e)}")
            raise

    def read_conversation_by_id(self, conversationId):
        query = "SELECT * FROM Conversation WHERE conversationId = %s"
        return self.repository.fetch_one(query, (conversationId,))

    def delete_conversation(self, conversationId):
        query = "UPDATE Conversation SET toDelete = TRUE WHERE conversationId = %s"
        self.repository.execute_query(query, (conversationId,))

    def update_conversation_timestamp(self, conversationId):
        """Aggiorna il timestamp updatedAt di una conversazione quando l'utente invia un messaggio"""
        query = "UPDATE Conversation SET updatedAt = CURRENT_TIMESTAMP WHERE conversationId = %s"
        self.repository.execute_query(query, (conversationId,))
        return True

    def add_message(self, conversationId, sender, content):
        query = "INSERT INTO Message (conversationId, sender, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING messageId"
        messageId = self.repository.fetch_one(query, (conversationId, sender, content))[0]
        
        return messageId

    def read_messages(self, conversationId):
        try:
            query = """
                SELECT m.*, 
                      f.feedbackId,
                      f.isHelpful,
                      f.content as feedback_content,
                      f.createdAt as feedback_createdAt
                FROM Message m 
                LEFT JOIN Feedback f ON m.messageId = f.messageId
                WHERE m.conversationId = %s 
                ORDER BY m.createdAt ASC
            """
            results = self.repository.fetch_all(query, (conversationId,))
            
            formatted_messages = []
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
                
                formatted_msg = {
                    'messageId': str(row[0]),
                    'conversationId': str(row[1]),
                    'sender': row[2],
                    'content': row[3],
                    'createdAt': str(row[4]),
                    'feedback': feedback
                }
                formatted_messages.append(formatted_msg)
            
            return formatted_messages
        except Exception as e:
            logging.error(f"Errore recupero messaggi per conversationId={conversationId}: {str(e)}")
            return []
    
    def read_feedback(self, messageId):
        query = "SELECT * FROM Feedback WHERE messageId = %s"
        query = "SELECT * FROM Feedback WHERE messageId = %s"
        return self.repository.fetch_all(query, (messageId,))
    
    def add_feedback(self, messageId, feedback, content=None):
        check_query = "SELECT COUNT(*) FROM Feedback WHERE messageId = %s"
        count = self.repository.fetch_one(check_query, (messageId,))[0]
        
        if count > 0:
            if content:
                query = "UPDATE Feedback SET isHelpful = %s, content = %s WHERE messageId = %s"
                self.repository.execute_query(query, (feedback == 1, content, messageId))
            else:
                query = "UPDATE Feedback SET isHelpful = %s WHERE messageId = %s"
                self.repository.execute_query(query, (feedback == 1, messageId))
        else:
            if content:
                query = "INSERT INTO Feedback (messageId, isHelpful, content, createdAt) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
                self.repository.execute_query(query, (messageId, feedback == 1, content))
            else:
                query = "INSERT INTO Feedback (messageId, isHelpful, createdAt) VALUES (%s, %s, CURRENT_TIMESTAMP)"
                self.repository.execute_query(query, (messageId, feedback == 1))
    
    def read_num_positive_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE isHelpful = TRUE"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
    
    def read_num_negative_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE isHelpful = FALSE"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
    
    def read_num_conversations(self):
        query = "SELECT COUNT(*) FROM Conversation"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
        
    def read_feedback_with_comments(self):
        """Recupera i feedback che hanno un commento (content non null)"""
        query = """
            SELECT f.feedbackId, f.messageId, f.isHelpful, f.content, f.createdAt, m.content as message_content 
            FROM Feedback f
            JOIN Message m ON f.messageId = m.messageId
            WHERE f.content IS NOT NULL AND f.content != ''
            ORDER BY f.createdAt DESC
            LIMIT 50
        """
        results = self.repository.fetch_all(query)
        
        formatted_feedback = []
        for row in results:
            feedback = {
                'feedbackId': str(row[0]),
                'messageId': str(row[1]),
                'type': 'positive' if row[2] else 'negative',
                'content': row[3],
                'createdAt': str(row[4]),
                'message_content': row[5][:100] + ('...' if len(row[5]) > 100 else '')  # Abbrevia il messaggio originale
            }
            formatted_feedback.append(feedback)
        
        return formatted_feedback