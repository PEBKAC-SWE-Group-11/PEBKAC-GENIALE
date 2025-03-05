from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from app.core.services.conversation_service import ConversationService
from app.adapters.services.embedding_service import EmbeddingService

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
API_KEY = "our-secret-api-key"

conversation_service = ConversationService()
embedding_service = EmbeddingService()

@app.route('/api/test', methods=['GET'])
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

@app.route('/api/question/<conversation_id>', methods=['POST'])
@require_api_key
def ask_question(conversation_id):
    question = request.json.get("question")
    messages = conversation_service.read_messages(conversation_id)
    text_to_embed = embedding_service.get_embeddings(question)
    response = conversation_service.get_llm_response(messages, question, text_to_embed)
    message_id = conversation_service.add_message(conversation_id, "assistant", response)
    return jsonify({"message_id": message_id}), 200

@app.route('/api/session/<session_id>', methods=['GET'])
@require_api_key
def api_read_session(session_id):
    try:
        session = conversation_service.read_session(session_id)
        if not session:
            conversation_service.create_session(session_id)
            session = conversation_service.read_session(session_id)
            return jsonify(session), 201
        return jsonify(session), 200
    except Exception as e:
        logging.error(f"Errore nella gestione della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation', methods=['POST'])
@require_api_key
def api_create_conversation():
    session_id = request.json.get('session_id')
    conversation = conversation_service.create_conversation(session_id)
    return jsonify({"conversation_id": conversation}), 201

@app.route('/api/conversation', methods=['GET'])
@require_api_key
def api_read_conversations():
    session_id = request.args.get('session_id')
    return jsonify(conversation_service.read_conversations(session_id)), 200

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
@require_api_key
def api_read_conversation_by_id(conversation_id):
    return jsonify(conversation_service.read_conversation_by_id(conversation_id)), 200

@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
@require_api_key
def api_delete_conversation(conversation_id):
    conversation_service.delete_conversation(conversation_id)
    return '', 204

@app.route('/api/message', methods=['POST'])
@require_api_key
def api_add_message():
    conversation_id = request.json.get('conversation_id')
    sender = request.json.get('sender')
    content = request.json.get('content')
    message_id = conversation_service.add_message(conversation_id, sender, content)
    return jsonify({"message_id": message_id}), 201

@app.route('/api/message', methods=['GET'])
@require_api_key
def api_read_messages():
    conversation_id = request.args.get('conversation_id')
    return jsonify(conversation_service.read_messages(conversation_id)), 200

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)