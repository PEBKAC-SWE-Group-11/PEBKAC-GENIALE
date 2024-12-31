import psycopg2 # type: ignore
import logging
import requests
"""
CERCA NEL DB VETTORIALE ELEMENTI "VICINI" AL PROMPT
"""
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

def get_database_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="localhost",
        port="54321"
    )

def search_similar_products(query_vector, top_k=1): # restituisce i primi k prodotti piu' simili al query_vector
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        query = """
            SELECT id, text_content, vector <-> %s::vector AS distance
            FROM test_table
            ORDER BY vector <-> %s::vector
            LIMIT %s;
        """     # "vector <-> query_vector" significa "distanza tra vector e query_vector"
        cursor.execute(query, (query_vector, query_vector, top_k))
        results = cursor.fetchall()

        for row in results:
            print(f"ID: {row[0]}, Distance: {row[2]}")
            print(f"Text Content: {row[1]}\n")
            return row[0], row[1]   # ritorno id del prodotto estratto + il suo json trascritto 

    except Exception as e:
        logging.error(f"Error querying database: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_embeddings(prompt):
    payload = {
        "model": "nomic-embed-text",
        "prompt": f"{prompt}"
    }

    response = requests.post(OLLAMA_EMBED_URL, json=payload)    # vettorializzo il prompt per confrontarlo con i vettori nel database

    if response.status_code == 200:
        query_vector = response.json().get("embedding")
        if not query_vector:
            raise ValueError("Failed to generate embedding for the query.")
    else:
        raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

    return search_similar_products(query_vector)
