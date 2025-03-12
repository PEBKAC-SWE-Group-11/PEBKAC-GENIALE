import psycopg2

def get_database_connection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="db",
        port="5432"
    )