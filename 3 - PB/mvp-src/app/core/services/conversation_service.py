from app.adapters.repositories.db_repository import DBRepository
from app.core.entities.entities import Session, Conversation, Message

class ConversationService:
    def __init__(self):
        self.repository = DBRepository()

    def create_session(self, session_id):
        query = "INSERT INTO Session (session_id, created_at) VALUES (%s, %s)"
        self.repository.execute_query(query, (session_id, Session(session_id).created_at))

    def read_session(self, session_id):
        query = "SELECT * FROM Session WHERE session_id = %s"
        return self.repository.fetch_one(query, (session_id,))

    def create_conversation(self, session_id):
        query = "INSERT INTO Conversation (session_id, created_at) VALUES (%s, CURRENT_TIMESTAMP) RETURNING conversation_id"
        return self.repository.fetch_one(query, (session_id,))[0]

    def read_conversations(self, session_id):
        query = "SELECT * FROM Conversation WHERE session_id = %s"
        return self.repository.fetch_all(query, (session_id,))

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
        query = "SELECT * FROM Feedback WHERE conversation_id = %s"
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