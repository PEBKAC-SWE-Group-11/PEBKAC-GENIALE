from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import logging
from local_model import get_llm_response 
from embedder import get_embeddings

from crud_conversations import (
    create_session, read_session,
    create_conversation, read_conversations, read_conversation_by_id, delete_conversation,
    add_message, read_messages,
)
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
API_KEY = "our-secret-api-key"

@app.route('/api/test', methods=['GET'])
def test_api():
    return {"message": "success"}, 200

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        print(f"Received API Key: {api_key}")  
        if api_key == API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function


# Existing API
@app.route('/api/question/<conversation_id>', methods=['POST'])
@require_api_key
def ask_question(conversation_id):
    question = request.json.get("question") 
    messages = read_messages(conversation_id)
            
    text_to_embed = get_embeddings(question)
    response = get_llm_response(messages, question, text_to_embed)

    message_id = add_message(conversation_id, "assistant", response)
        
    return jsonify({"message_id": message_id}), 200

@app.route('/api/session/<session_id>', methods=['GET'])
@require_api_key
def api_read_session(session_id):
    try:
        session = read_session(session_id)
        if not session:
            logging.info(f"Sessione {session_id} non trovata, la creo")
            create_session(session_id)
            session = read_session(session_id)
            return jsonify(session), 201  
        
        return jsonify(session), 200
        
    except Exception as e:
        logging.error(f"Errore nella gestione della sessione: {str(e)}")
        return jsonify({"error": str(e)}), 500

# API for Conversations
@app.route('/api/conversation', methods=['POST'])
@require_api_key
def api_create_conversation():  
    session_id = request.json.get('session_id')
    conversation = create_conversation(session_id)
    return jsonify({"conversation_id": conversation}), 201

@app.route('/api/conversation', methods=['GET'])
@require_api_key
def api_read_conversations():
    session_id = request.args.get('session_id')
    return jsonify(read_conversations(session_id)), 200

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
@require_api_key
def api_read_conversation_by_id():
    conversation_id = request.args.get('conversation_id')
    return jsonify(read_conversation_by_id(conversation_id)), 200

@app.route('/api/conversation/<conversation_id>', methods=['DELETE'])
@require_api_key
def api_delete_conversation(conversation_id):
    delete_conversation(conversation_id)
    return '', 204


# API for Messages
@app.route('/api/message', methods=['POST'])
@require_api_key
def api_add_message():
    conversation_id = request.json.get('conversation_id')
    sender = request.json.get('sender')
    content = request.json.get('content')
    message_id = add_message(conversation_id, sender, content)
    return jsonify({"message_id": message_id}), 201

@app.route('/api/message', methods=['GET'])
@require_api_key
def api_read_messages():
    conversation_id = request.args.get('conversation_id')
    return jsonify(read_messages(conversation_id)), 200

# Error handling
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {e}")
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
