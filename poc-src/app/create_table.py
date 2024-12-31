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
        host="localhost",
        port="54321"
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

    connection.commit()

    logging.info(f"Tabelle creata con SUCCESSO.")
except Exception as e:
    logging.error(f"Errore durante la connessione o la creazione della tabella: {e}", exc_info=True)
finally:
    if connection:
        cursor.close()
        connection.close()
