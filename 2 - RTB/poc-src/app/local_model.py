import ollama  # type: ignore
import logging
from typing import List, Dict

"""
INTERROGA IL LLM, DANDOGLI DOMANDA, STORIA DELLA CHAT E CONTESTO ESTRATTO DAL DB
"""

def get_llm_response(messages: List[Dict], question: str, text_to_embed: str) -> str:
    model = 'llama3.2:1b'
    
    # Formatta i messaggi precedenti nel formato corretto per ollama
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg["sender"],  # converte "user"/"assistant" nel formato ollama
            "content": msg["content"]
        })
    
    # Aggiungi il nuovo contesto e la domanda
    system_context = f"Usa questo contesto per rispondere: {text_to_embed}"
    formatted_messages.extend([
        {"role": "system", "content": system_context},
        {"role": "user", "content": question}
    ])
    
    logging.info(f"Sending messages to Ollama: {formatted_messages}")
    
    try:
        stream = ollama.chat(
            model=model, 
            messages=formatted_messages, 
            stream=True
        )
        
        response = ""
        for chunk in stream:
            if chunk and "message" in chunk and "content" in chunk["message"]:
                response += chunk["message"]["content"]
        
        # Se c'è ancora il problema dell'intestazione, controlliamo prima
        logging.info(f"Raw response from Ollama: {response}")
        
        # Rimuovi l'intestazione solo se necessario e presente
        if response.startswith("Assistant: "):
            response = response[11:]  # rimuove "Assistant: "
        
        logging.info(f"Cleaned response: {response}")
        return response
        
    except Exception as e:
        logging.error(f"Error with Ollama API: {e}", exc_info=True)
        return "Mi dispiace, si è verificato un errore nella generazione della risposta."
