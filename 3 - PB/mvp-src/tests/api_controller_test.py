import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.adapters.controllers.api_controller import flask_app as app, API_KEY
from app.adapters.services import embedding_service

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
        mock_conversation_service.add_message.return_value = "message_id"

        response = self.app.post(
            '/api/question/1',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"question": "What is AI?"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message_id": "message_id"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_create_conversation(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation")
        mock_conversation_service.create_conversation.return_value = "conversation_id"

        response = self.app.post(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"session_id": "1"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"conversation_id": "conversation_id"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_create_conversation_missing_session_id(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation con session_id mancante")
        response = self.app.post(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            data=json.dumps({}),  # No session_id provided
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "session_id mancante"})

    


    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_conversations(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation con query string")
        mock_conversation_service.read_conversations.return_value = [{"conversation_id": "1"}]

        response = self.app.get(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            query_string={'session_id': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"conversation_id": "1"}])

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_conversation_by_id(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation/1")
        mock_conversation_service.read_conversation_by_id.return_value = {"conversation_id": "1"}

        response = self.app.get(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"conversation_id": "1"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_delete_conversation(self, mock_conversation_service):
        print("Test per l'endpoint DELETE /api/conversation/1")
        response = self.app.delete(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 204)

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_delete_conversation(self, mock_conversation_service):
        print("Test per l'endpoint DELETE /api/conversation/1 con errore interno")
        mock_conversation_service.delete_conversation.side_effect = Exception("Internal Server Error")

        response = self.app.delete(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Internal Server Error"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_add_message(self, mock_conversation_service):
        print("Test per l'endpoint POST /api/message")
        mock_conversation_service.add_message.return_value = "message_id"

        response = self.app.post(
            '/api/message',
            headers={'x-api-key': API_KEY},
            data=json.dumps({
                "conversation_id": "1",
                "sender": "user",
                "content": "Hello"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message_id": "message_id"})

    # @patch('app.adapters.controllers.api_controller.conversation_service')
    # def test_api_add_message(self, mock_conversation_service):
    #     print("Test per l'endpoint POST /api/message con errore interno")
    #     mock_conversation_service.add_message.side_effect = Exception("Internal Server Error")

    #     response = self.app.post(
    #         '/api/message',
    #         headers={'x-api-key': API_KEY},
    #         data=json.dumps({
    #             "conversation_id": "1",
    #             "sender": "user",
    #             "content": "Hello"
    #         }),
    #         content_type='application/json'
    #     )

    #     self.assertEqual(response.status_code, 500)
    #     self.assertEqual(response.json, {"error": "Internal Server Error"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_messages(self, mock_conversation_service):
        print("Test per l'endpoint GET /api/message")
        mock_conversation_service.read_messages.return_value = [{"message_id": "1"}]

        response = self.app.get(
            '/api/message',
            headers={'x-api-key': API_KEY},
            query_string={'conversation_id': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"message_id": "1"}])

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_read_conversations_missing_session_id(self, mock_conversation_service):
        print("Test per l'endpoint /api/conversation con query string mancante")
        response = self.app.get(
            '/api/conversation',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "session_id mancante"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_delete_conversation_not_found(self, mock_conversation_service):
        print("Test per l'endpoint DELETE /api/conversation/1 con conversazione non trovata")
        mock_conversation_service.delete_conversation.side_effect = Exception("Conversation not found")

        response = self.app.delete(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Conversation not found"})

    @patch('app.adapters.controllers.api_controller.conversation_service')
    def test_api_add_message_missing_fields(self, mock_conversation_service):
        print("Test per l'endpoint POST /api/message con campi mancanti")
        response = self.app.post(
            '/api/message',
            headers={'x-api-key': API_KEY},
            data=json.dumps({
                "conversation_id": "1",
                "sender": "user"
                # Missing "content"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing required fields"})

    # @patch('app.adapters.services.embedding_service.EmbeddingService.get_embeddings')
    # def test_getEmbedding_exception(self, mock_get_embeddings):
    #     print("Test per eccezione durante la generazione dell'embedding")
    #     mock_get_embeddings.side_effect = Exception("Errore durante la generazione dell'embedding")

    #     with self.assertRaises(Exception) as context:
    #         embedding_service.get_embeddings("test data")

    #     self.assertIn("Errore durante la generazione dell'embedding", str(context.exception))



if __name__ == '__main__':
    unittest.main()