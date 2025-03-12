import json
import logging
import psycopg2
import embeddinglocal
from connection_db import get_db_connection

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Inserisci i dati tecnici
        for key, value in product['technical_data'].items():
            cursor.execute("""
                INSERT INTO TechnicalData (product_id, key, value)
                VALUES (%s, %s, %s);
            """, (product['id'], key, value))
        
        # Inserisci le immagini
        for image in product.get('images', []):
            cursor.execute("""
                INSERT INTO Image (product_id, url)
                VALUES (%s, %s);
            """, (product['id'], image))
        
        # Inserisci i documenti
        for doc in product.get('documentation', []):
            cursor.execute("""
                INSERT INTO Documentation (product_id, url)
                VALUES (%s, %s);
            """, (product['id'], doc))

    except Exception as e:
        logger.error(f"Errore durante l'inserimento del prodotto {product.get('id')}: {e}")
        raise

def write_products_in_DB(product_file, connection):
    """Inserisce i prodotti nel database usando una connessione esistente"""
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Lettura del file JSON
        with open(product_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Inserimento dei dati nel database
        for product in data['vimar_datas']:
            insert_product(cursor, product)

        # Commit delle modifiche
        connection.commit()
        logger.info("Dati inseriti con successo nel database.")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei dati: {e}", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()