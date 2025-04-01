import logging
from psycopg2.extensions import connection as pgConnection
from EmbeddingLocal import getEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getVectorDimension() -> int:
    """Ritorna la dimensione del vettore di embedding"""
    #return len(getEmbedding("test"))
    return 1024

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
                description TEXT,
                etim TEXT,
                idVector vector({vectorDim}),
                idTitleVector vector({vectorDim}),
                idTitleDescrVector vector({vectorDim})
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
                productId TEXT NOT NULL,
                CONSTRAINT unique_title_product UNIQUE (title, productId),
                FOREIGN KEY (productId) REFERENCES Product(id) ON DELETE CASCADE  -- Chiave esterna verso Product
            );''',

        # Tabella Session per gestire le sessioni utente
            '''CREATE TABLE IF NOT EXISTS Session (
                sessionId TEXT PRIMARY KEY,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                isActive BOOLEAN DEFAULT TRUE
            );''',
        # Tabella Conversation per gestire le conversazioni
            '''CREATE TABLE IF NOT EXISTS Conversation (
                conversationId SERIAL PRIMARY KEY,
                sessionId TEXT NOT NULL,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                toDelete BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (sessionId) REFERENCES Session(sessionId) ON DELETE CASCADE
            );''',
            
            # Tabella Message per gestire i messaggi
            '''CREATE TABLE IF NOT EXISTS Message (
                messageId SERIAL PRIMARY KEY,
                conversationId INTEGER NOT NULL,
                sender TEXT CHECK(sender IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversationId) REFERENCES Conversation(conversationId) ON DELETE CASCADE
            );''',
            
            # Tabella Feedback per gestire i feedback sui messaggi
            '''CREATE TABLE IF NOT EXISTS Feedback (
                feedbackId SERIAL PRIMARY KEY,
                messageId INTEGER NOT NULL,
                isHelpful BOOLEAN NOT NULL,  -- true per positivo, false per negativo
                content TEXT, -- Aggiungiamo il campo per i commenti (può essere NULL)
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (messageId) REFERENCES Message(messageId) ON DELETE CASCADE
            );'''
        ] 
        # Esegue le query di creazione
        for query in tables:
            logger.info(f"Esecuzione query: {query[:50]}...")
            cursor.execute(query)
            
        # Creazione del trigger per disattivare sessioni inattive dopo 30 giorni
        triggerSql = '''
        -- Tabella per tracciare l'ultimo controllo delle sessioni
        CREATE TABLE IF NOT EXISTS SessionCheck (
            lastCheck TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Inserisce un record iniziale se non esiste
        INSERT INTO SessionCheck 
        SELECT CURRENT_TIMESTAMP 
        WHERE NOT EXISTS (SELECT 1 FROM SessionCheck);
        
        -- Funzione che verifica le sessioni inattive solo una volta ogni 10 giorni
        CREATE OR REPLACE FUNCTION check_session_activity() RETURNS TRIGGER AS $$
        DECLARE
            lastCheck_time TIMESTAMP;
            check_interval INTERVAL := '10 days';
        BEGIN
            -- Ottiene la data dell'ultimo controllo
            SELECT lastCheck INTO lastCheck_time FROM SessionCheck LIMIT 1;
            
            -- Controlla se sono passati almeno 10 giorni dall'ultimo controllo
            IF lastCheck_time IS NULL OR lastCheck_time < (NOW() - check_interval) THEN
                -- Aggiorna le sessioni inattive
                UPDATE Session 
                SET isActive = FALSE 
                WHERE updatedAt < NOW() - INTERVAL '30 days';
                
                -- Aggiorna il timestamp dell'ultimo controllo
                UPDATE SessionCheck SET lastCheck = CURRENT_TIMESTAMP;
                
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
        
        cursor.execute(triggerSql)
        logger.info("Trigger per sessioni inattive creato con successo")
            
        connection.commit()
        logger.info("Tutte le tabelle sono state create con successo")
        
    except Exception as e:
        logger.error(f"Errore durante la creazione delle tabelle: {e}", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()