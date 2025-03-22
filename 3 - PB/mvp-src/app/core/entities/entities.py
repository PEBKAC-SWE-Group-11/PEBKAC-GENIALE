from datetime import datetime

class Session:
    def __init__(self, session_id: str, created_at: str, updated_at: str = None, is_active: bool = True):
        self.session_id = session_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active


class Conversation:
    def __init__(self, conversation_id: str, session_id: str, created_at: str, updated_at: str, to_delete: bool = False):
        self.conversation_id = conversation_id
        self.session_id = session_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.to_delete = to_delete


class Message:
    def __init__(self, message_id: str, conversation_id: str, sender: str, content: str, created_at: str):
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.sender = sender
        self.content = content
        self.created_at = created_at


class Feedback:
    def __init__(self, feedback_id: str, message_id: str, is_helpful: bool, content: str = None, created_at: str = None):
        self.feedback_id = feedback_id
        self.message_id = message_id
        self.is_helpful = is_helpful
        self.content = content
        self.created_at = created_at 