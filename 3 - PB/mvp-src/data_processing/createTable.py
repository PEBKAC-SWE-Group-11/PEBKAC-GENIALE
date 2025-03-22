import logging
import json
from typing import Any
from psycopg2.extensions import connection as pgConnection
from embeddingLocal import getEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getVectorDimension() -> int:
    """Ritorna la dimensione del vettore di embedding"""
    return len(getEmbedding("test"))

def createTables(connection: pgConnection) -> None:
    """Crea le tabelle nel database usando una connessione esistente"""
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Determina la dimensione del vettore
        vectorDim = getVectorDimension()
        
        logger.info("Inizio creazione tabelle...")

        # Lista delle query per la creazione delle tabelle
        tables = [
            
            # Tabella Product per gestire la RAG
            f'''CREATE TABLE IF NOT EXISTS Product (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                desciption TEXT,
                etim TEXT,
                id_vector vector({vectorDim}),
                idtitle_vector vector({vectorDim}),
                idtitledescr_vector vector({vectorDim})
            );''',

            # Tabella Chunk con dimensione vettore dinamica
            f'''CREATE TABLE IF NOT EXISTS Chunk(
                id SERIAL PRIMARY KEY,
                filename VARCHAR(200),
                chunk TEXT NOT NULL,
                embedding vector({vectorDim}) NOT NULL,
                CONSTRAINT unique_filename_chunk UNIQUE (filename, chunk) 

            );''',

            # Tabella Document per gestire i documenti
            f'''CREATE TABLE IF NOT EXISTS Document (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                product_id TEXT NOT NULL,
                CONSTRAINT unique_title_product UNIQUE (title, product_id),
                FOREIGN KEY (product_id) REFERENCES Product(id) ON DELETE CASCADE  -- Chiave esterna verso Product
            );''',

        # Tabella Session per gestire le sessioni utente
            '''CREATE TABLE IF NOT EXISTS Session (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );''',
        # Tabella Conversation per gestire le conversazioni
            '''CREATE TABLE IF NOT EXISTS Conversation (
                conversation_id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                to_delete BOOLEAN DEFAULT FALSE,
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
                content TEXT, -- Aggiungiamo il campo per i commenti (può essere NULL)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES Message(message_id) ON DELETE CASCADE
            );'''
        ] 
        # Esegue le query di creazione
        for query in tables:
            logger.info(f"Esecuzione query: {query[:50]}...")
            cursor.execute(query)
            
        # Creazione del trigger per disattivare sessioni inattive dopo 30 giorni
        trigger_sql = '''
        -- Tabella per tracciare l'ultimo controllo delle sessioni
        CREATE TABLE IF NOT EXISTS SessionCheck (
            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Inserisce un record iniziale se non esiste
        INSERT INTO SessionCheck 
        SELECT CURRENT_TIMESTAMP 
        WHERE NOT EXISTS (SELECT 1 FROM SessionCheck);
        
        -- Funzione che verifica le sessioni inattive solo una volta ogni 10 giorni
        CREATE OR REPLACE FUNCTION check_session_activity() RETURNS TRIGGER AS $$
        DECLARE
            last_check_time TIMESTAMP;
            check_interval INTERVAL := '10 days';
        BEGIN
            -- Ottiene la data dell'ultimo controllo
            SELECT last_check INTO last_check_time FROM SessionCheck LIMIT 1;
            
            -- Controlla se sono passati almeno 10 giorni dall'ultimo controllo
            IF last_check_time IS NULL OR last_check_time < (NOW() - check_interval) THEN
                -- Aggiorna le sessioni inattive
                UPDATE Session 
                SET is_active = FALSE 
                WHERE updated_at < NOW() - INTERVAL '30 days';
                
                -- Aggiorna il timestamp dell'ultimo controllo
                UPDATE SessionCheck SET last_check = CURRENT_TIMESTAMP;
                
                RAISE NOTICE 'Controllo sessioni inattive eseguito a %', NOW();
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trigger_check_session_activity ON Session;
        
        -- Crea un trigger che si attiva solo una volta per transazione
        CREATE TRIGGER trigger_check_session_activity
            AFTER UPDATE ON Session
            FOR EACH STATEMENT
            EXECUTE FUNCTION check_session_activity();
        '''
        
        cursor.execute(trigger_sql)
        logger.info("Trigger per sessioni inattive creato con successo")
            
        connection.commit()
        logger.info("Tutte le tabelle sono state create con successo")
        
    except Exception as e:
        logger.error(f"Errore durante la creazione delle tabelle: {e}", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()