import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.adapters.controllers.api_controller import app, API_KEY

class TestAPIController(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_test_api(self):
        print("Test per l'endpoint /api/test")
        response = self.app.get('/api/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "success"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    @patch('app.adapters.controllers.api_controller.embedding_service')
    def test_ask_question(self, mock_embedding_service, mock_conversation_service):
        print("Test per l'endpoint /api/question/1")
        mock_conversation_service.read_messages.return_value = []
        mock_embedding_service.get_embeddings.return_value = "embedded_text"
        mock_conversation_service.get_llm_response.return_value = "response"
        mock_conversation_service.add_message.return_value = "messageId"

        response = self.app.post(
            '/api/question/1',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"question": "What is AI?"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"messageId": "messageId"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_session(self, mock_conversation_service):
        print("Test per l'endpoint /api/session/1")
        mock_conversation_service.read_session.return_value = {"sessionId": "1"}

        response = self.app.get(
            '/api/session/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"sessionId": "1"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_create_conversation(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation")
        mock_conversation_service.create_conversation.return_value = "conversationId"

        response = self.app.post(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"sessionId": "1"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"conversationId": "conversationId"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_conversations(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation con query string")
        mock_conversation_service.read_conversations.return_value = [{"conversationId": "1"}]

        response = self.app.get(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            query_string={'sessionId': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"conversationId": "1"}])

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_conversation_by_id(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation/1")
        mock_conversation_service.read_conversation_by_id.return_value = {"conversationId": "1"}

        response = self.app.get(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"conversationId": "1"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_delete_conversation(self, mock_conversation_service):
        print("Test per l'endpoint DELETE /api/conversation/1")
        response = self.app.delete(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 204)

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_add_message(self, mock_conversation_service):
        print("Test per l'endpoint POST /api/message")
        mock_conversation_service.add_message.return_value = "messageId"

        response = self.app.post(
            '/api/message',
            headers={'x-api-key': API_KEY},
            data=json.dumps({
                "conversationId": "1",
                "sender": "user",
                "content": "Hello"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"messageId": "messageId"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_messages(self, mock_conversation_service):
        print("Test per l'endpoint GET /api/message")
        mock_conversation_service.read_messages.return_value = [{"messageId": "1"}]

        response = self.app.get(
            '/api/message',
            headers={'x-api-key': API_KEY},
            query_string={'conversationId': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"messageId": "1"}])

if __name__ == '__main__':
    unittest.main()