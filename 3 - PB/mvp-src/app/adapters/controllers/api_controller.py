from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from app.core.services.conversation_service import ConversationService
from app.adapters.services.embedding_service import EmbeddingService
from app.infrastructure.http.api import flask_app


CORS(flask_app, resources={r"/*": {"origins": "http://localhost:4200"}})
API_KEY = "our-secret-api-key"

conversation_service = ConversationService()
embedding_service = EmbeddingService()

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

@flask_app.route('/api/question/<conversation_id>', methods=['POST'])
@require_api_key
def ask_question(conversation_id):
    question = request.json.get("question")
    messages = conversation_service.read_messages(conversation_id)
    text_to_embed = embedding_service.get_embeddings(question)
    response = conversation_service.get_llm_response(messages, question, text_to_embed)
    message_id = conversation_service.add_message(conversation_id, "assistant", response)
    return jsonify({"message_id": message_id}), 200


@flask_app.route('/api/session', methods=['POST'])
@require_api_key
def api_create_session():
    try:
        session_id = conversation_service.create_session()
        return jsonify({"session_id": session_id}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/session/<session_id>', methods=['PUT'])
@require_api_key
def api_update_session(session_id):
    try:
        success = conversation_service.update_session(session_id)
        return jsonify({"success": success}), 200
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation', methods=['POST'])
@require_api_key
def api_create_conversation():
    try:
        session_id = request.json.get('session_id')
        if not session_id:
            return jsonify({"error": "session_id mancante"}), 400
            
        conversation = conversation_service.create_conversation(session_id)
        return jsonify({"conversation_id": conversation}), 201
    except Exception as e:
        logging.error(f"Errore nella creazione della conversazione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation', methods=['GET'])
@require_api_key
def api_read_conversations():
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({"error": "session_id mancante"}), 400
            
        conversations = conversation_service.read_conversations(session_id)
        return jsonify(conversations), 200
    except Exception as e:
        logging.error(f"Errore nel recupero delle conversazioni: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation/<conversation_id>', methods=['GET'])
@require_api_key
def api_read_conversation_by_id(conversation_id):
    return jsonify(conversation_service.read_conversation_by_id(conversation_id)), 200

@flask_app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
@require_api_key
def api_delete_conversation(conversation_id):
    try:
        print(f"Deleting conversation with ID: {conversation_id}")
        conversation_service.delete_conversation(conversation_id)
        print(f"Deleted conversation with ID: {conversation_id}")
        return '', 204
    except Exception as e:
        print(f"Error deleting conversation with ID: {conversation_id} - {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/conversation/<conversation_id>/update', methods=['PUT'])
@require_api_key
def api_update_conversation_timestamp(conversation_id):
    try:
        success = conversation_service.update_conversation_timestamp(conversation_id)
        return jsonify({"success": success}), 200
    except Exception as e:
        logging.error(f"Errore nell'aggiornamento della conversazione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/api/message', methods=['POST'])
@require_api_key
def api_add_message():
    conversation_id = request.json.get('conversation_id')
    sender = request.json.get('sender')
    content = request.json.get('content')
    message_id = conversation_service.add_message(conversation_id, sender, content)
    return jsonify({"message_id": message_id}), 201

@flask_app.route('/api/message', methods=['GET'])
@require_api_key
def api_read_messages():
    conversation_id = request.args.get('conversation_id')
    return jsonify(conversation_service.read_messages(conversation_id)), 200

@flask_app.route('/api/feedback/<message_id>', methods=['GET'])
@require_api_key
def api_read_feedback_by_message_id(message_id):
    return jsonify(conversation_service.read_feedback(message_id)), 200

@flask_app.route('/api/feedback', methods=['POST'])
@require_api_key
def api_add_feedback():
    message_id = request.json.get('message_id')
    feedback_value = request.json.get('feedback_value')
    content = request.json.get('content')  # Può essere None
    
    feedback_id = conversation_service.add_feedback(message_id, feedback_value, content)
    return jsonify({"message_id": message_id}), 201

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