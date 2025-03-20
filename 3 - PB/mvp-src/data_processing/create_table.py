import logging
import json
from typing import Any
from psycopg2.extensions import connection as pg_connection
from embeddinglocal import getEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_vector_dimension(json_path: str) -> int:
   """Ritorna la dimensione del vettore di embedding"""
   return len(getEmbedding("test"))


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
                to_delete BOOLEAN NOT NULL DEFAULT false,  -- true per positivo, false per negativo
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
                content TEXT,
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

            # Tabella Product per gestire la RAG
            f'''CREATE TABLE IF NOT EXISTS Document (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                product_id TEXT NOT NULL
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
