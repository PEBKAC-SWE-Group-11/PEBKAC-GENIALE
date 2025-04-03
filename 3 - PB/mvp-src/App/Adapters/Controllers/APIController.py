from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from App.Core.Services.ConversationService import ConversationService
from App.Infrastructure.Http.API import flaskApp
from App.Adapters.Services.ContextExtractorService import ContextExtractorService
from App.Adapters.Services.LLMResponseService import LLMResponseService

CORS(flaskApp, resources={r"/*": {"origins": "http://localhost:4200"}})
API_KEY = "our-secret-api-key"

conversationService = ConversationService()
contextExtractor = ContextExtractorService()
llmResponse = LLMResponseService()

@flaskApp.route('/api/test', methods=['GET'])
def testAPI():
    return {"message": "success"}, 200

def requireAPIKey(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        APIKey = request.headers.get('x-api-key')
        if APIKey == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decoratedFunction

@flaskApp.route('/api/question/<conversationId>', methods=['POST'])
@requireAPIKey
def askQuestion(conversationId):
    try:
        question = request.json.get("question")
        textsToEmbed, etimToEmbed = contextExtractor.processUserInput(question)
        print(f"#####Texts to embed: {textsToEmbed}#####")
        print(f"#####Etim to embed: {etimToEmbed}#####")
        messages = conversationService.readMessages(conversationId)
        print(f"#####Messages: {messages}#####")
        response = llmResponse.getLlmResponse(messages, question, textsToEmbed, etimToEmbed)
        print(f"#####Response: {response}#####")
        #userMessageId = conversationService.addMessage(conversationId, "user", question)
        assistantMessageId = conversationService.addMessage(conversationId, "assistant", response)
        return jsonify({"messageId": assistantMessageId}), 200
    except Exception as e:
        print(f"#####Error in askQuestion: {str(e)}#####")
        return jsonify({"error": str(e)}), 500

@flaskApp.route('/api/session', methods=['POST'])
@requireAPIKey
def apiCreateSession():
    try:
        sessionId = conversationService.createSession()
        return jsonify({"sessionId": sessionId}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@flaskApp.route('/api/session/<sessionId>', methods=['GET'])
@requireAPIKey
def apiReadSession(sessionId):
    try:
        session = conversationService.readSession(sessionId)
        return jsonify(session), 200
    except Exception as e:
        logging.error(f"Errore nel recupero della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@flaskApp.route('/api/session/<sessionId>', methods=['PUT'])
@requireAPIKey
def apiUpdateSession(sessionId):
    try:
        success = conversationService.updateSession(sessionId)
        return jsonify({"success": success}), 200
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flaskApp.route('/api/conversation', methods=['POST'])
@requireAPIKey
def apiCreateConversation():
    try:
        sessionId = request.json.get('sessionId')
        if not sessionId:
            return jsonify({"error": "sessionId mancante"}), 400
            
        conversation = conversationService.createConversation(sessionId)
        return jsonify({"conversationId": conversation}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della conversazione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flaskApp.route('/api/conversation', methods=['GET'])
@requireAPIKey
def apiReadConversations():
    try:
        sessionId = request.args.get('sessionId')
        if not sessionId:
            return jsonify({"error": "sessionId mancante"}), 400
            
        conversations = conversationService.readConversations(sessionId)
        return jsonify(conversations), 200
    except Exception as e:
        logging.error(f"Errore nel recupero delle conversazioni: {str(e)}")
        return jsonify({"error": str(e)}), 500

#@flaskApp.route('/api/conversation/<conversationId>', methods=['GET'])
#@requireAPIKey
#def apiReadConversationById(conversationId):
#    return jsonify(conversationService.readConversationById(conversationId)), 200

@flaskApp.route('/api/conversation/<conversationId>', methods=['DELETE'])
@requireAPIKey
def apiDeleteConversation(conversationId):
    try:
        print(f"Deleting conversation with ID: {conversationId}")
        conversationService.deleteConversation(conversationId)
        print(f"Deleted conversation with ID: {conversationId}")
        return '', 204
    except Exception as e:
        print(f"Error deleting conversation with ID: {conversationId} - {str(e)}")
        return jsonify({"error": str(e)}), 500

#@flaskApp.route('/api/conversation/<conversationId>/update', methods=['PUT'])
#@requireAPIKey
#def apiUpdateConversationTimestamp(conversationId):
#    try:
#        success = conversationService.updateConversationTimestamp(conversationId)
#        return jsonify({"success": success}), 200
#    except Exception as e:
#        logging.error(f"Errore nell'aggiornamento della conversazione: {str(e)}")
#        return jsonify({"error": str(e)}), 500

@flaskApp.route('/api/message', methods=['POST'])
@requireAPIKey
def apiAddMessage():
    conversationId = request.json.get('conversationId')
    sender = request.json.get('sender')
    content = request.json.get('content')

    if not conversationId or not sender or not content:
        return jsonify({"error": "Missing required fields"}), 400

    messageId = conversationService.addMessage(conversationId, sender, content)
    return jsonify({"messageId": messageId}), 201

@flaskApp.route('/api/message', methods=['GET'])
@requireAPIKey
def apiReadMessages():
    conversationId = request.args.get('conversationId')
    return jsonify(conversationService.readMessages(conversationId)), 200

#@flaskApp.route('/api/feedback/<messageId>', methods=['GET'])
#@requireAPIKey
#def apiReadFeedbackByMessageId(messageId):
#    return jsonify(conversationService.readFeedback(messageId)), 200

@flaskApp.route('/api/feedback', methods=['POST'])
@requireAPIKey
def apiAddFeedback():
    messageId = request.json.get('messageId')
    feedbackValue = request.json.get('feedbackValue')
    content = request.json.get('content') 
    
    conversationService.addFeedback(messageId, feedbackValue, content)
    return jsonify({"messageId": messageId}), 201

@flaskApp.route('/api/dashboard/numPositive', methods=['GET'])
@requireAPIKey
def apiReadNumPositiveFeedback():
    try:
        numPositiveFedback = conversationService.readNumPositiveFeedback()
        return jsonify({"numPositiveFeedback": numPositiveFedback}), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback positivi: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flaskApp.route('/api/dashboard/numNegative', methods=['GET'])
@requireAPIKey
def apiReadNumNegativeFeedback():
    try:
        numNegativeFeedback = conversationService.readNumNegativeFeedback()
        return jsonify({"numNegativeFeedback": numNegativeFeedback}), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback negativi: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@flaskApp.route('/api/dashboard/numConversations', methods=['GET'])
@requireAPIKey
def apiReadNumConversations():
    try:
        numConversations = conversationService.readNumConversations()
        return jsonify({"numConversations": numConversations}), 200
    except Exception as e:
        logging.error(f"Errore recupero numero conversazioni: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@flaskApp.route('/api/dashboard/feedbackComments', methods=['GET'])
@requireAPIKey
def apiReadFeedbackWithComments():
    try:
        feedbackComments = conversationService.readFeedbackWithComments()
        return jsonify(feedbackComments), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback con commenti: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flaskApp.errorhandler(Exception)
def handleException(e):
    flaskApp.logger.error(f"An error occurred: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    flaskApp.run(host='0.0.0.0', port=5001)
