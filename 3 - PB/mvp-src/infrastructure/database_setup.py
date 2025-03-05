import psycopg2
import logging
import requests


class DatabaseSetup:
    def __init__(self, embed_url: str = "http://localhost:11434/api/embeddings"):
        self.embed_url = embed_url

    def create_tables(self):
        connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )
        cursor = connection.cursor()

        try:
            payload = {
                "model": "nomic-embed-text",
                "prompt": f"lorem ipsum"
            }

            response = requests.post(self.embed_url, json=payload)

            if response.status_code == 200:
                query_vector = response.json().get("embedding")
                if not query_vector:
                    raise ValueError("Failed to generate embedding for the query.")
            else:
                raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

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
            connection.commit()

        except Exception as e:
            logging.error(f"Error creating tables: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close() 