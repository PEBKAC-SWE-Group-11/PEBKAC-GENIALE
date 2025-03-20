import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getEmbedding(text):
    """Ottiene l'embedding del testo usando l'API di Ollama"""
    try:
        url = "http://app:11434/api/embeddings"
        payload = {
            "model": "mxbai-embed-large",
            "prompt": text
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("embedding")
        else:
            raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Errore durante la generazione dell'embedding: {e}")
        raise