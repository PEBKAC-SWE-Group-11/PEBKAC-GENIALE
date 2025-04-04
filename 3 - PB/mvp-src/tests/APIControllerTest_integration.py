import unittest
import json
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from App.Adapters.Controllers.APIController import flaskApp as app, API_KEY

class TestAPIController(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def testTestApi(self):
        print("Test per l'endpoint /api/test: Verifica che l'endpoint restituisca correttamente il messaggio di successo")
        response = self.app.get('/api/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "success"})

    @patch('App.Adapters.Controllers.APIcontroller.conversationService')
    @patch('App.Adapters.Controllers.APIController.embedding_service')
    def testAskQuestion(self, mockEmbeddingService, mockConversationService):
        print("Test per l'endpoint /api/question/1: Verifica che l'endpoint gestisca correttamente una richiesta di domanda")
        mockConversationService.readMessages.return_value = []
        mockEmbeddingService.get_embeddings.return_value = "embedded_text"
        mockConversationService.get_llm_response.return_value = "response"
        mockConversationService.add_message.return_value = "messageId"

        response = self.app.post(
            '/api/question/1',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"question": "What is AI?"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"messageId": "messageId"})

    @patch('App.Adapters.Controllers.APIController.conversationService')
    def testApiCreateConversation(self, mockConversationService):
        print("Test per l'endpoint /api/conversation: Verifica che l'endpoint crei correttamente una nuova conversazione")
        mockConversationService.createConversation.return_value = "conversationId"

        response = self.app.post(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            data=json.dumps({"sessionId": "1"}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"conversationId": "conversationId"})

    @patch('App.Adapters.Controllers.APIController.conversationService')
    def testApiReadConversations(self, mockConversationService):
        print("Test per l'endpoint /api/conversation con query string: Verifica che l'endpoint recuperi correttamente tutte le conversazioni associate a una sessione")
        mockConversationService.readConversations.return_value = [{"conversationId": "1"}]

        response = self.app.get(
            '/api/conversation',
            headers={'x-api-key': API_KEY},
            query_string={'sessionId': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"conversationId": "1"}])

    # @patch('App.Adapters.Controllers.APIController.conversationService')
    # def testApiReadConversationById(self, mockConversationService):
    #     print("Test per l'endpoint /api/conversation/1: Verifica che l'endpoint recuperi correttamente una conversazione tramite il suo ID")
    #     mockConversationService.readConversation_by_id.return_value = {"conversationId": "1"}

    #     response = self.app.get(
    #         '/api/conversation/1',
    #         headers={'x-api-key': API_KEY}
    #     )

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json, {"conversationId": "1"})

    @patch('App.Adapters.Controllers.APIController.conversationService')
    def testApiDeleteConversation(self, mockConversationService):
        print("Test per l'endpoint DELETE /api/conversation/1: Verifica che l'endpoint elimini correttamente una conversazione")
        response = self.app.delete(
            '/api/conversation/1',
            headers={'x-api-key': API_KEY}
        )

        self.assertEqual(response.status_code, 204)

    @patch('App.Adapters.Controllers.APIController.conversationService')
    def testApiAddMessage(self, mockConversationService):
        print("Test per l'endpoint POST /api/message: Verifica che l'endpoint aggiunga correttamente un nuovo messaggio a una conversazione")
        mockConversationService.addMessage.return_value = "messageId"

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

    @patch('App.Adapters.Controllers.APIController.conversationService')
    def testApiReadMessages(self, mockConversationService):
        print("Test per l'endpoint GET /api/message: Verifica che l'endpoint recuperi correttamente tutti i messaggi associati a una conversazione")
        mockConversationService.readMessages.return_value = [{"messageId": "1"}]

        response = self.app.get(
            '/api/message',
            headers={'x-api-key': API_KEY},
            query_string={'conversationId': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"messageId": "1"}])

if __name__ == '__main__':
    unittest.main()