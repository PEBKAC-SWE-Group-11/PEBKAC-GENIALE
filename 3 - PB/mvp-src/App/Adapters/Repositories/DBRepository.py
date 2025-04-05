import psycopg2
from App.Core.Ports.RepositoryPort import RepositoryPort

class DBRepository(RepositoryPort):
    def __init__(self):
        self.connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="pebkac",
            host="db",
            port="5432"
        )

    def executeQuery(self, query, params=None):
        cursor = self.connection.cursor()
        print(f"Query: {query}")
        print(f"Params: {params}")
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

    def fetchOne(self, query, params=None):
        cursor = self.executeQuery(query, params)
        return cursor.fetchone()

    def fetchAll(self, query, params=None):
        cursor = self.executeQuery(query, params)
        return cursor.fetchall()

    def close(self):
        self.connection.close()