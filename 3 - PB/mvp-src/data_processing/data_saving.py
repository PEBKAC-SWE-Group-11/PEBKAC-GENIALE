import json
import logging
import psycopg2
import embeddinglocal
from connection_db import get_db_connection
import re
from typing import Any
from psycopg2.extensions import connection as pg_connection

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_chunks(text, max_chunk_size=500):
    """Divide il testo in chunk di dimensione massima specificata"""
    # Rimuove caratteri speciali e spazi multipli
    text = re.sub(r'\s+', ' ', text)
    
    # Divide il testo in parole
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 per lo spazio
        if current_size + word_size > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def insert_chunks(cursor, product_id, product):
    """Inserisce i chunk di un prodotto nel database"""
    try:
        # Crea il testo completo del prodotto
        full_text = f"{product.get('title', '')} {product.get('description', '')} {json.dumps(product.get('technical_data', {}))}"
        
        # Genera i chunk
        chunks = create_chunks(full_text)
        
        # Inserisci ogni chunk con il suo embedding
        for chunk in chunks:
            cursor.execute("""
                INSERT INTO Chunk (product_id, titolo_doc, chunk, embedding)
                VALUES (%s, %s, %s, %s);
            """, (
                product_id,
                product.get('title', ''),
                chunk,
                embeddinglocal.get_embedding(chunk)
            ))
        
        logger.info(f"Inseriti {len(chunks)} chunk per il prodotto {product_id}")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei chunk per il prodotto {product_id}: {e}")
        raise

def insert_chunks_from_file(cursor: Any, chunks: list) -> None:
    """
    Inserisce i chunk nel database
    Args:
        cursor: cursore del database
        chunks: lista di chunk da inserire
    """
    try:
        total_chunks = len(chunks)
        logger.info(f"Trovati {total_chunks} chunk da inserire")
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Elaborazione chunk {i}/{total_chunks}")
            cursor.execute("""
                INSERT INTO Chunk (product_id, filename, chunk, embedding)
                VALUES (%s, %s, %s, %s);
            """, (
                chunk['id'],
                chunk['filename'],
                chunk['chunk'],
                chunk['vector']
            ))
        
        logger.info("Tutti i chunk sono stati inseriti con successo nel database.")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei chunk: {e}", exc_info=True)
        raise

# Funzione per creare la tabella se non esiste
def create_table(cursor):
    #TODO: Controllare se con un testo riempitivo ha senso, altrimenti occorre estrarre prima un prodotto per sapere la dimensione
    vector_dim = len(embeddinglocal.get_embedding("lorem ipsum"))
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
        embedding vector(''' + str(vector_dim) + ''')
        );
        '''
    cursor.execute(query)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TechnicalData (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        key TEXT NOT NULL,
        value TEXT NOT NULL
        );
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Image (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        url TEXT NOT NULL
        );
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Documentation (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR(50) REFERENCES Product(product_id),
        url TEXT NOT NULL
        );
        ''')

def insert_product(cursor, product):
    """Inserisce un singolo prodotto nel database"""
    try:
        # Inserisci i dati del prodotto
        cursor.execute('''
            INSERT INTO Product (product_id, title, description, price, gruppo, classe, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING;
        ''', (
            product['id'],
            product['title'],
            product['description'],
            product['price'],
            product['technical_data'].get('Gruppo'),
            product['technical_data'].get('Classe'),
            embeddinglocal.get_embedding(f"{product.get('id')} {product.get('title')} {product.get('description')} {product.get('price')} "
                                     f"{json.dumps(product.get('technical_data'))} {json.dumps(product.get('images'))} {json.dumps(product.get('documentation'))}")
        ))
        logger.info(f"Inserito prodotto con ID: {product['id']}")
        
        # Inserisci i dati tecnici
        for key, value in product['technical_data'].items():
            cursor.execute("""
                INSERT INTO TechnicalData (product_id, key, value)
                VALUES (%s, %s, %s);
            """, (product['id'], key, value))
        logger.info(f"Inseriti dati tecnici per il prodotto {product['id']}")
        
        # Inserisci le immagini
        for image in product.get('images', []):
            cursor.execute("""
                INSERT INTO Image (product_id, url)
                VALUES (%s, %s);
            """, (product['id'], image))
        logger.info(f"Inserite immagini per il prodotto {product['id']}")
        
        # Inserisci i documenti
        for doc in product.get('documentation', []):
            cursor.execute("""
                INSERT INTO Documentation (product_id, url)
                VALUES (%s, %s);
            """, (product['id'], doc))
        logger.info(f"Inseriti documenti per il prodotto {product['id']}")
        
        # Inserisci i chunk
        insert_chunks(cursor, product['id'], product)

    except Exception as e:
        logger.error(f"Errore durante l'inserimento del prodotto {product.get('id')}: {e}")
        raise

def write_products_in_DB(chunk_file: str, connection: pg_connection) -> None:
    """
    Inserisce i chunk nel database usando una connessione esistente
    Args:
        chunk_file: percorso al file JSON contenente i chunk con embedding
        connection: connessione al database
    """
    cursor = None
    try:
        # Disabilita autocommit per la transazione
        connection.autocommit = False
        cursor = connection.cursor()
        
        logger.info("Inizio transazione")
        logger.info(f"Lettura del file chunk {chunk_file}")
        
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # Inserimento chunks
        insert_chunks_from_file(cursor, chunks)

        # Commit della transazione
        connection.commit()
        logger.info("Transazione completata con successo")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei dati: {e}", exc_info=True)
        logger.info("Esecuzione rollback della transazione")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.autocommit = True

if __name__ == "__main__":
    try:
        connection = get_db_connection()
        write_products_in_DB('json_data/chunkfile.json', connection)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del programma: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Connessione al database chiusa")