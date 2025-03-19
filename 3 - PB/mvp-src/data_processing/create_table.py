import logging
import json
from typing import Any
from psycopg2.extensions import connection as pg_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_vector_dimension(json_path: str) -> int:
    """Determina la dimensione del vettore dal primo chunk nel file JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            if not chunks:
                raise ValueError("File JSON vuoto")
            vector_dim = len(chunks[0]['vector'])
            logger.info(f"Dimensione del vettore rilevata: {vector_dim}")
            return vector_dim
    except Exception as e:
        logger.error(f"Errore nella lettura della dimensione del vettore: {e}")
        raise

def create_tables(connection: pg_connection, json_path: str) -> None:
    """Crea le tabelle nel database usando una connessione esistente"""
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Determina la dimensione del vettore
        vector_dim = get_vector_dimension(json_path)
        
        logger.info("Inizio creazione tabelle...")

        # Lista delle query per la creazione delle tabelle
        tables = [
            # Tabella Chunk con dimensione vettore dinamica
            f'''CREATE TABLE IF NOT EXISTS Chunk(
                id SERIAL PRIMARY KEY,
                filename VARCHAR(200),
                chunk TEXT NOT NULL,
                embedding vector({vector_dim}) NOT NULL
            );''',
            
            # Tabella Session per gestire le sessioni utente
            '''CREATE TABLE IF NOT EXISTS Session (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );''',
            
            # Tabella Conversation per gestire le conversazioni
            '''CREATE TABLE IF NOT EXISTS Conversation (
                conversation_id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE
            );''',
            
            # Tabella Message per gestire i messaggi
            '''CREATE TABLE IF NOT EXISTS Message (
                message_id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                sender TEXT CHECK(sender IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES Conversation(conversation_id) ON DELETE CASCADE
            );''',
            
            # Tabella Feedback per gestire i feedback sui messaggi
            '''CREATE TABLE IF NOT EXISTS Feedback (
                feedback_id SERIAL PRIMARY KEY,
                message_id INTEGER NOT NULL,
                is_helpful BOOLEAN NOT NULL,  -- true per positivo, false per negativo
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES Message(message_id) ON DELETE CASCADE
            );''',

            # Tabella Product per gestire la RAG
            f'''CREATE TABLE IF NOT EXISTS Product (
                product_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                desciption TEXT,
                etim TEXT,
                id_vector vector({vector_dim}),
                idtitle_vector vector({vector_dim}),
                idtitledescr_vector vector({vector_dim})
            );'''
            
        ]

        # Esegue le query di creazione
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
