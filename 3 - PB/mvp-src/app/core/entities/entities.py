from datetime import datetime

class Session:
    def __init__(self, session_id, created_at=None):
        self.session_id = session_id
        self.created_at = created_at or datetime.now()


class Conversation:
    def __init__(self, conversation_id: str, session_id: str, created_at: str):
        self.conversation_id = conversation_id
        self.session_id = session_id
        self.created_at = created_at


class Message:
    def __init__(self, message_id: str, conversation_id: str, sender: str, content: str, created_at: str):
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.sender = sender
        self.content = content
        self.created_at = created_at 