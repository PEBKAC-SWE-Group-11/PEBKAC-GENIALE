import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_embedding(text):
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

def import_data(connection):
    try:
        # Percorso corretto all'interno del container
        write_products_in_DB('/app/data_processing/json_data/data_reduced.json', connection)
        logger.info("Importazione dati completata con successo")
    except Exception as e:
        logger.error(f"Errore durante l'importazione dei dati: {e}", exc_info=True)
        raise 