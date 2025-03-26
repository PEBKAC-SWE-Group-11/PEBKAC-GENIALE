from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from app.core.services.conversation_service import ConversationService
from app.infrastructure.http.api import flask_app
from app.adapters.services.contextExtractorService import contextExtractorService
from app.adapters.services.llmResponseService import llmResponseService
from app.infrastructure.http.api import flask_app


CORS(flask_app, resources={r"/*": {"origins": "http://localhost:4200"}})
API_KEY = "our-secret-api-key"

conversation_service = ConversationService()
contextExtractor = contextExtractorService()
llmResponse = llmResponseService()

@flask_app.route('/api/test', methods=['GET'])
def test_api():
    return {"message": "success"}, 200

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

@flask_app.route('/api/question/<conversationId>', methods=['POST'])
@require_api_key
def ask_question(conversationId):
    try:
        question = request.json.get("question")
        textsToEmbed, etimToEmbed = contextExtractor.processUserInput(question)
        print(f"#####Texts to embed: {textsToEmbed}#####")
        print(f"#####Etim to embed: {etimToEmbed}#####")
        messages = conversation_service.read_messages(conversationId)
        print(f"#####Messages: {messages}#####")
        response = llmResponse.getLlmResponse(messages, question, textsToEmbed, etimToEmbed)
        print(f"#####Response: {response}#####")
        messageId = conversation_service.add_message(conversationId, "assistant", response)
        return jsonify({"messageId": messageId}), 200
    except Exception as e:
        print(f"#####Error in ask_question: {str(e)}#####")
        return jsonify({"error": str(e)}), 500
    # question = request.json.get("question")
    # messages = conversation_service.read_messages(conversationId)
    # text_to_embed = embedding_service.get_embeddings(question)
    # response = conversation_service.get_llm_response(messages, question, text_to_embed)
    # messageId = conversation_service.add_message(conversationId, "assistant", response)
    # return jsonify({"messageId": messageId}), 200


@flask_app.route('/api/session', methods=['POST'])
@require_api_key
def api_create_session():
    try:
        sessionId = conversation_service.create_session()
        return jsonify({"sessionId": sessionId}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/session/<sessionId>', methods=['PUT'])
@require_api_key
def api_update_session(sessionId):
    try:
        success = conversation_service.update_session(sessionId)
        return jsonify({"success": success}), 200
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation', methods=['POST'])
@require_api_key
def api_create_conversation():
    try:
        sessionId = request.json.get('sessionId')
        if not sessionId:
            return jsonify({"error": "sessionId mancante"}), 400
            
        conversation = conversation_service.create_conversation(sessionId)
        return jsonify({"conversationId": conversation}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della conversazione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation', methods=['GET'])
@require_api_key
def api_read_conversations():
    try:
        sessionId = request.args.get('sessionId')
        if not sessionId:
            return jsonify({"error": "sessionId mancante"}), 400
            
        conversations = conversation_service.read_conversations(sessionId)
        return jsonify(conversations), 200
    except Exception as e:
        logging.error(f"Errore nel recupero delle conversazioni: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation/<conversationId>', methods=['GET'])
@require_api_key
def api_read_conversation_by_id(conversationId):
    return jsonify(conversation_service.read_conversation_by_id(conversationId)), 200

@flask_app.route('/api/conversation/<conversationId>', methods=['DELETE'])
@require_api_key
def api_delete_conversation(conversationId):
    try:
        print(f"Deleting conversation with ID: {conversationId}")
        conversation_service.delete_conversation(conversationId)
        print(f"Deleted conversation with ID: {conversationId}")
        return '', 204
    except Exception as e:
        print(f"Error deleting conversation with ID: {conversationId} - {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation/<conversationId>/update', methods=['PUT'])
@require_api_key
def api_update_conversation_timestamp(conversationId):
    try:
        success = conversation_service.update_conversation_timestamp(conversationId)
        return jsonify({"success": success}), 200
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della conversazione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/message', methods=['POST'])
@require_api_key
def api_add_message():
    conversationId = request.json.get('conversationId')
    sender = request.json.get('sender')
    content = request.json.get('content')
    messageId = conversation_service.add_message(conversationId, sender, content)
    return jsonify({"messageId": messageId}), 201

@flask_app.route('/api/message', methods=['GET'])
@require_api_key
def api_read_messages():
    conversationId = request.args.get('conversationId')
    return jsonify(conversation_service.read_messages(conversationId)), 200

@flask_app.route('/api/feedback/<messageId>', methods=['GET'])
@require_api_key
def api_read_feedback_by_messageId(messageId):
    return jsonify(conversation_service.read_feedback(messageId)), 200

@flask_app.route('/api/feedback', methods=['POST'])
@require_api_key
def api_add_feedback():
    messageId = request.json.get('messageId')
    feedback_value = request.json.get('feedback_value')
    content = request.json.get('content')  # Può essere None
    
    feedbackId = conversation_service.add_feedback(messageId, feedback_value, content)
    return jsonify({"messageId": messageId}), 201

@flask_app.route('/api/dashboard/num_positive', methods=['GET'])
@require_api_key
def api_read_num_positive_feedback():
    try:
        num_positive_feedback = conversation_service.read_num_positive_feedback()
        return jsonify({"num_positive_feedback": num_positive_feedback}), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback positivi: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/dashboard/num_negative', methods=['GET'])
@require_api_key
def api_read_num_negative_feedback():
    try:
        num_negative_feedback = conversation_service.read_num_negative_feedback()
        return jsonify({"num_negative_feedback": num_negative_feedback}), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback negativi: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@flask_app.route('/api/dashboard/num_conversations', methods=['GET'])
@require_api_key
def api_read_num_conversations():
    try:
        num_conversations = conversation_service.read_num_conversations()
        return jsonify({"num_conversations": num_conversations}), 200
    except Exception as e:
        logging.error(f"Errore recupero numero conversazioni: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@flask_app.route('/api/dashboard/feedback_comments', methods=['GET'])
@require_api_key
def api_read_feedback_with_comments():
    try:
        feedback_comments = conversation_service.read_feedback_with_comments()
        return jsonify(feedback_comments), 200
    except Exception as e:
        logging.error(f"Errore recupero feedback con commenti: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.errorhandler(Exception)
def handle_exception(e):
    flask_app.logger.error(f"An error occurred: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5001)
