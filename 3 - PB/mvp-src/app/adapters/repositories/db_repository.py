import psycopg2
from app.core.ports.repository_port import RepositoryPort

class DBRepository(RepositoryPort):
    def __init__(self):
        self.connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        print(f"Query: {query}")
        print(f"Params: {params})")
        try:
            cursor.execute(query, params)
            print("Query COMMITTED successfully")
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            print("Query ROLLED BACK")
            return cursor

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def close(self):
        self.connection.close()