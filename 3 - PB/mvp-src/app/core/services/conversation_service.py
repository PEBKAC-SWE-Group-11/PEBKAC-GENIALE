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
        session_id = str(uuid.uuid4())
        logger.info("SESSION: ", session_id)
        query = "INSERT INTO Session (session_id, created_at, updated_at, is_active) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)"
        self.repository.execute_query(query, (session_id,))
        return session_id

    def read_session(self, session_id):
        query = "SELECT * FROM Session WHERE session_id = %s"
        return self.repository.fetch_one(query, (session_id,))

    def update_session(self, session_id):
        """Aggiorna il timestamp updated_at di una sessione per mantenerla attiva"""
        query = "UPDATE Session SET updated_at = CURRENT_TIMESTAMP WHERE session_id = %s"
        self.repository.execute_query(query, (session_id,))
        return True

    def create_conversation(self, session_id):
        try:
            query = "INSERT INTO Conversation (session_id, created_at, updated_at, to_delete) VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE) RETURNING conversation_id"
            return self.repository.fetch_one(query, (session_id,))[0]
        except Exception as e:
            logging.error(f"Errore creazione conversazione per session_id={session_id}: {str(e)}")
            raise

    def read_conversations(self, session_id):
        try:
            query = """
                SELECT * FROM Conversation 
                WHERE session_id = %s AND (to_delete = FALSE OR to_delete IS NULL) 
                ORDER BY updated_at DESC
            """
            results = self.repository.fetch_all(query, (session_id,))
            
            formatted_conversations = []
            for row in results:
                if isinstance(row, dict):
                    formatted_conversations.append(row)
                else:
                    formatted_conv = {
                        'conversation_id': row[0],
                        'session_id': row[1],
                        'created_at': row[2],
                        'updated_at': row[3],
                        'to_delete': row[4] if len(row) > 4 else False
                    }
                    formatted_conversations.append(formatted_conv)
            
            return formatted_conversations
        except Exception as e:
            logging.error(f"Errore recupero conversazioni per session_id={session_id}: {str(e)}")
            raise

    def read_conversation_by_id(self, conversation_id):
        query = "SELECT * FROM Conversation WHERE conversation_id = %s"
        return self.repository.fetch_one(query, (conversation_id,))

    def delete_conversation(self, conversation_id):
        query = "UPDATE Conversation SET to_delete = TRUE WHERE conversation_id = %s"
        self.repository.execute_query(query, (conversation_id,))

    def update_conversation_timestamp(self, conversation_id):
        """Aggiorna il timestamp updated_at di una conversazione quando l'utente invia un messaggio"""
        query = "UPDATE Conversation SET updated_at = CURRENT_TIMESTAMP WHERE conversation_id = %s"
        self.repository.execute_query(query, (conversation_id,))
        return True

    def add_message(self, conversation_id, sender, content):
        query = "INSERT INTO Message (conversation_id, sender, content, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING message_id"
        message_id = self.repository.fetch_one(query, (conversation_id, sender, content))[0]
        
        return message_id

    def read_messages(self, conversation_id):
        try:
            query = """
                SELECT m.*, 
                      f.feedback_id,
                      f.is_helpful,
                      f.content as feedback_content,
                      f.created_at as feedback_created_at
                FROM Message m 
                LEFT JOIN Feedback f ON m.message_id = f.message_id
                WHERE m.conversation_id = %s 
                ORDER BY m.created_at ASC
            """
            results = self.repository.fetch_all(query, (conversation_id,))
            
            formatted_messages = []
            for row in results:
                feedback = None
                if len(row) > 5 and row[5] is not None:
                    feedback = {
                        'feedback_id': str(row[5]),
                        'message_id': str(row[0]),
                        'type': 'positive' if row[6] else 'negative',
                        'content': row[7],
                        'created_at': str(row[8]) if row[8] else None
                    }
                
                formatted_msg = {
                    'message_id': str(row[0]),
                    'conversation_id': str(row[1]),
                    'sender': row[2],
                    'content': row[3],
                    'created_at': str(row[4]),
                    'feedback': feedback
                }
                formatted_messages.append(formatted_msg)
            
            return formatted_messages
        except Exception as e:
            logging.error(f"Errore recupero messaggi per conversation_id={conversation_id}: {str(e)}")
            return []
    
    def read_feedback(self, message_id):
        query = "SELECT * FROM Feedback WHERE message_id = %s"
        query = "SELECT * FROM Feedback WHERE message_id = %s"
        return self.repository.fetch_all(query, (message_id,))
    
    def add_feedback(self, message_id, feedback, content=None):
        check_query = "SELECT COUNT(*) FROM Feedback WHERE message_id = %s"
        count = self.repository.fetch_one(check_query, (message_id,))[0]
        
        if count > 0:
            if content:
                query = "UPDATE Feedback SET is_helpful = %s, content = %s WHERE message_id = %s"
                self.repository.execute_query(query, (feedback == 1, content, message_id))
            else:
                query = "UPDATE Feedback SET is_helpful = %s WHERE message_id = %s"
                self.repository.execute_query(query, (feedback == 1, message_id))
        else:
            if content:
                query = "INSERT INTO Feedback (message_id, is_helpful, content, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)"
                self.repository.execute_query(query, (message_id, feedback == 1, content))
            else:
                query = "INSERT INTO Feedback (message_id, is_helpful, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)"
                self.repository.execute_query(query, (message_id, feedback == 1))
    
    def read_num_positive_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE is_helpful = TRUE"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
    
    def read_num_negative_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE is_helpful = FALSE"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
    
    def read_num_conversations(self):
        query = "SELECT COUNT(*) FROM Conversation"
        result = self.repository.fetch_one(query)
        return result[0] if result else 0
        
    def read_feedback_with_comments(self):
        """Recupera i feedback che hanno un commento (content non null)"""
        query = """
            SELECT f.feedback_id, f.message_id, f.is_helpful, f.content, f.created_at, m.content as message_content 
            FROM Feedback f
            JOIN Message m ON f.message_id = m.message_id
            WHERE f.content IS NOT NULL AND f.content != ''
            ORDER BY f.created_at DESC
            LIMIT 50
        """
        results = self.repository.fetch_all(query)
        
        formatted_feedback = []
        for row in results:
            feedback = {
                'feedback_id': str(row[0]),
                'message_id': str(row[1]),
                'type': 'positive' if row[2] else 'negative',
                'content': row[3],
                'created_at': str(row[4]),
                'message_content': row[5][:100] + ('...' if len(row[5]) > 100 else '')  # Abbrevia il messaggio originale
            }
            formatted_feedback.append(feedback)
        
        return formatted_feedback