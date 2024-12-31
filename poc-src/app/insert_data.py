import psycopg2 # type: ignore
import logging
import os
import json
import requests
"""
POPOLA LA TABELLA NEL DB, GENERANDO I VETTORI USATI PER L'EMBEDDING
"""
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

JSON_DIR = "./json_data"

def insert():
    connection = get_database_connection()
    cursor = connection.cursor()
    
    file_path = os.path.join(JSON_DIR, 'data_reduced.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
           
    try:
        for product in data['vimar_datas']:
            print(f"Inserting product {product['id']}...")
            insert_product(cursor, product)
            connection.commit()

    except Exception as e:
        logging.error(f"Error inserting products: {e}")
    finally:
        if cursor:
            print("Committing changes...")
            cursor.close()
        if connection:
            connection.close()

    return 

def get_database_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="localhost",
        port="54321"
    )

def get_embedding(product):
    json_text = json.dumps(product, ensure_ascii=False)    
    payload = {
        "model": "nomic-embed-text",
        "prompt": json_text
    }
    response = requests.post(OLLAMA_EMBED_URL, json=payload)    # interroga il modello di embedding sul json trascritto

    if response.status_code == 200:
        vector = response.json().get("embedding")
        if vector:
            return vector
    return []    

def escape_single_quotes(value):
    return value.replace("'", "''") if isinstance(value, str) else value

def insert_product(cursor, product):
    query = (
        f"INSERT INTO Product (product_id, title, description, price, gruppo, classe, embedding) VALUES "
        f"('{escape_single_quotes(product['id'])}', '{escape_single_quotes(product['title'])}', '{escape_single_quotes(product['description'])}', '{escape_single_quotes(product['price'])}', "
        f"'{escape_single_quotes(product['technical_data'].get('Gruppo'))}', '{escape_single_quotes(product['technical_data'].get('Classe'))}', '{escape_single_quotes(get_embedding(product))}') "
        f"ON CONFLICT (product_id) DO NOTHING;"
    )
    print(query)
    cursor.execute(query)
    print(f"Product {product['id']} inserted successfully.")
    
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


if __name__ == "__main__":
    insert()