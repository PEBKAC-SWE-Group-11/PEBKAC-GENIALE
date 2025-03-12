import json
import logging
import psycopg2
import json 
import embeddinglocal

# Configura il logging
logging.basicConfig(level=logging.INFO)

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

# Funzione per inserire i dati nel database
def insert_product(cursor, product):

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




    #insert_query = '''
    #INSERT INTO products (id, title, description, price, technical_data, images, documentation, embedding)
    #VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #ON CONFLICT (id) DO NOTHING;
    #'''
    #cursor.execute(insert_query, (
    #    product['id'],
    #    product.get('title'),
    #    product.get('description'),
    #    product.get('price'),
    #    json.dumps(product.get('technical_data', {})),  # Default to empty dict if not present
    #    json.dumps(product.get('images', [])),          # Default to empty list if not present
    #    json.dumps(product.get('documentation', {})),    # Default to empty dict if not present
    #    embeddings.get_embedding(f"{product.get('id')} {product.get('title')} {product.get('description')} {product.get('price')} "
    #                             f"{json.dumps(product.get('technical_data'))} {json.dumps(product.get('images'))} {json.dumps(product.get('documentation'))}")
    #))

def write_products_in_DB(product_file):
    # Connessione al database
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="localhost",
        port="54321"
    )
    cursor = connection.cursor()

    # Creazione della tabella
    create_table(cursor)
    connection.commit()

    # Lettura del file JSON
    with open(product_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Inserimento dei dati nel database
    for product in data['vimar_datas']:
        insert_product(cursor, product)

    # Commit delle modifiche
    connection.commit()

    # Chiusura della connessione
    cursor.close()
    connection.close()
    logging.info("Dati inseriti con successo nel database.")