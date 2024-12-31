import ollama  # type: ignore
"""
INTERROGA IL LLM, DANDOGLI DOMANDA, STORIA DELLA CHAT E CONTESTO ESTRATTO DAL DB
"""
def get_llm_response(conversation_pile, question, text_to_embed):
    model = 'llama3.2:1b'
    embedding_context = f"Usa questo contesto per rispondere: {text_to_embed}"
    
    messages = conversation_pile + [
        {"role": "user", "content": question},
        {"role": "system", "content": embedding_context}
    ]
    
    try:
        stream = ollama.chat(model=model, messages=messages, stream=True)
        response = ""
        for chunk in stream:
            response += chunk["message"]["content"]
        
        response = response[46:]    # boh non riesco a togliere l'intestazione
        return response
    except Exception as e:
        print(f"Error with Ollama API: {e}")
        return "There was an error processing your request."
