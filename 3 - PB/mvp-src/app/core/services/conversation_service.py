import uuid
from app.adapters.repositories.db_repository import DBRepository
from app.core.entities.entities import Session, Conversation, Message
import logging

class ConversationService:
    def __init__(self):
        self.repository = DBRepository()

    def create_session(self):
        session_id = str(uuid.uuid4())
        print("SESSION: ", session_id)
        query = "INSERT INTO Session (session_id, created_at) VALUES (%s, CURRENT_TIMESTAMP)"
        self.repository.execute_query(query, (session_id,))
        return session_id

    def read_session(self, session_id):
        query = "SELECT * FROM Session WHERE session_id = %s"
        return self.repository.fetch_one(query, (session_id,))

    def create_conversation(self, session_id):
        try:
            query = "INSERT INTO Conversation (session_id, created_at) VALUES (%s, CURRENT_TIMESTAMP) RETURNING conversation_id"
            return self.repository.fetch_one(query, (session_id,))[0]
        except Exception as e:
            logging.error(f"Errore creazione conversazione per session_id={session_id}: {str(e)}")
            raise

    def read_conversations(self, session_id):
        try:
            query = "SELECT * FROM Conversation WHERE session_id = %s ORDER BY created_at DESC"
            results = self.repository.fetch_all(query, (session_id,))
            
            # Trasforma i risultati in dizionari con nomi di proprietà corretti
            formatted_conversations = []
            for row in results:
                # Verifica se è già un dizionario
                if isinstance(row, dict):
                    formatted_conversations.append(row)
                else:
                    # Assumiamo che i campi siano nell'ordine: conversation_id, session_id, created_at
                    formatted_conv = {
                        'conversation_id': row[0],  # Probabile intero
                        'session_id': row[1],       # Stringa
                        'created_at': row[2]        # Timestamp
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
        query = "DELETE FROM Conversation WHERE conversation_id = %s"
        self.repository.execute_query(query, (conversation_id,))

    def add_message(self, conversation_id, sender, content):
        query = "INSERT INTO Message (conversation_id, sender, content, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING message_id"
        return self.repository.fetch_one(query, (conversation_id, sender, content))[0]

    def read_messages(self, conversation_id):
        query = "SELECT * FROM Message WHERE conversation_id = %s"
        return self.repository.fetch_all(query, (conversation_id,))
    
    def read_feedback(self, message_id):
        query = "SELECT * FROM Feedback WHERE message_id = %s"
        return self.repository.fetch_all(query, (message_id,))
    
    def add_feedback(self, message_id, feedback):
        query = "INSERT INTO Feedback (message_id, feedback, created_at) VALUES (%s, %s, CURRENT_TIMESTAMP)"
        self.repository.execute_query(query, (message_id, feedback))
    
    #Cruscotto amministratore
    def read_num_positive_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE feedback = 1"
        return self.repository.fetch_all(query)
    
    def read_num_negative_feedback(self):
        query = "SELECT COUNT(*) FROM Feedback WHERE feedback = 0"
        return self.repository.fetch_all(query)
    
    def read_num_conversations(self):
        query = "SELECT COUNT(*) FROM Conversation"
        return self.repository.fetch_all(query)