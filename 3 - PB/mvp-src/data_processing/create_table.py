import logging
import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables(connection):
    """Crea le tabelle nel database usando una connessione esistente"""
    cursor = None
    try:
        cursor = connection.cursor()

        # # Test dell'embedding - TEMPORANEAMENTE COMMENTATO
        # payload = {
        #     "model": "nomic-embed-text",
        #     "prompt": f"lorem ipsum"
        # }

        # response = requests.post(OLLAMA_EMBED_URL, json=payload)
        # if response.status_code == 200:
        #     query_vector = response.json().get("embedding")
        #     if not query_vector:
        #         raise ValueError("Failed to generate embedding for the query.")
        # else:
        #     raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

        logger.info("Inizio creazione tabelle...")

        # Crea le tabelle
        tables = [
            '''CREATE TABLE IF NOT EXISTS Product (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                price TEXT,
                gruppo TEXT,
                classe TEXT,
                embedding vector(768)
            );''',
            '''CREATE TABLE IF NOT EXISTS TechnicalData (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES Product(product_id),
                key TEXT NOT NULL,
                value TEXT NOT NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS Image (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES Product(product_id),
                url TEXT NOT NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS Documentation (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES Product(product_id),
                url TEXT NOT NULL
            );''',
            '''CREATE TABLE IF NOT EXISTS Chunk(
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) REFERENCES Product(product_id),
                titolo_doc VARCHAR(200),
                chunk TEXT NOT NULL,
                embedding vector(768)
            );''',
            '''CREATE TABLE IF NOT EXISTS Session (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            '''CREATE TABLE IF NOT EXISTS Conversation (
                conversation_id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES Session (session_id) ON DELETE CASCADE
            );''',
            '''CREATE TABLE IF NOT EXISTS Message (
                message_id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                sender TEXT CHECK(sender IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES Conversation (conversation_id) ON DELETE CASCADE
            );''',
            '''CREATE TABLE IF NOT EXISTS Feedback (
                feedback_id SERIAL PRIMARY KEY,
                message_id INTEGER NOT NULL,
                is_helpful BOOLEAN NOT NULL,  -- true per positivo, false per negativo
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES Message (message_id) ON DELETE CASCADE
            );'''
        ]

        for query in tables:
            logger.info(f"Esecuzione query: {query[:50]}...")
            cursor.execute(query)
            
        connection.commit()
        logger.info("Tutte le tabelle sono state create con successo")
        
    except Exception as e:
        logger.error(f"Errore durante la creazione delle tabelle: {e}", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()
