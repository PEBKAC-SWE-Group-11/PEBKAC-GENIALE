class Session:
    def __init__(self, sessionId: str, createdAt: str, updatedAt: str = None, isActive: bool = True):
        self.sessionId = sessionId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.isActive = isActive


class Conversation:
    def __init__(self, conversationId: str, sessionId: str, createdAt: str, updatedAt: str, toDelete: bool = False):
        self.conversationId = conversationId
        self.sessionId = sessionId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.toDelete = toDelete


class Message:
    def __init__(self, messageId: str, conversationId: str, sender: str, content: str, createdAt: str):
        self.messageId = messageId
        self.conversationId = conversationId
        self.sender = sender
        self.content = content
        self.createdAt = createdAt


class Feedback:
    def __init__(self, feedbackId: str, messageId: str, isHelpful: bool, content: str = None, createdAt: str = None):
        self.feedbackId = feedbackId
        self.messageId = messageId
        self.isHelpful = isHelpful
        self.content = content
        self.createdAt = createdAt 