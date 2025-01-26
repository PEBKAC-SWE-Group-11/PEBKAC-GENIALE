import psycopg2 # type: ignore
import logging
import requests

""""
CREA LA TABELLA NEL DB:

"""
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
logging.basicConfig(level=logging.INFO)

try:
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="db",
        port="5432"
    )
    cursor = connection.cursor()

    #TODO: Controllare se con un testo riempitivo ha senso, altrimenti occorre estrarre prima un prodotto per sapere la dimensione
    payload = {
        "model": "nomic-embed-text",
        "prompt": f"lorem ipsum"
    }

    response = requests.post(OLLAMA_EMBED_URL, json=payload)    # vettorializzo il prompt per confrontarlo con i vettori nel database

    if response.status_code == 200:
        query_vector = response.json().get("embedding")
        if not query_vector:
            raise ValueError("Failed to generate embedding for the query.")
    else:
        raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

    # Crea le tabelle
    query = '''
        CREATE TABLE IF NOT EXISTS Product (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        price TEXT,
        gruppo TEXT,
        classe TEXT,
        embedding vector(768)
        );
        '''
    cursor.execute(query)
    logging.info(f"Tabella PRODUCT creata con successo.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TechnicalData (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        key TEXT NOT NULL,
        value TEXT NOT NULL
        );
        ''')
    logging.info(f"Tabella TECHNICALDATA creata con successo.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Image (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        url TEXT NOT NULL
        );
        ''')
    logging.info(f"Tabella IMAGE creata con successo.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Documentation (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        url TEXT NOT NULL
        );
        ''')
    logging.info(f"Tabella DOCUMENTATION creata con successo.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chunk(
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        titolo_doc VARCHAR(200),
        chunk TEXT NOT NULL,
        embedding vector(768)
        );
        ''')
    logging.info(f"Tabella CHUNK creata con successo.")

    cursor.execute('''
         CREATE TABLE IF NOT EXISTS Session (
        session_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
    logging.info(f"Tabella SESSION creata con successo.")

    cursor.execute('''
       CREATE TABLE IF NOT EXISTS Conversation (
        conversation_id SERIAL PRIMARY KEY,
        session_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES Session (session_id) ON DELETE CASCADE
        );
        ''')
    logging.info(f"Tabella CONVERSATION creata con successo.")

    cursor.execute('''
       CREATE TABLE IF NOT EXISTS Message (
        message_id SERIAL PRIMARY KEY,
        conversation_id INTEGER NOT NULL,
        sender TEXT CHECK(sender IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES Conversation (conversation_id) ON DELETE CASCADE
        );
        ''')
    logging.info(f"Tabella MESSAGE creata con successo.")
    
    connection.commit()

    logging.info(f"TABELLE creata con SUCCESSO.")
except Exception as e:
    logging.error(f"Errore durante la connessione o la creazione della tabella: {e}", exc_info=True)
finally:
    if connection:
        cursor.close()
        connection.close()
