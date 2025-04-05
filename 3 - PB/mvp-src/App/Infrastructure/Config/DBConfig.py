import psycopg2

def getDatabaseConnection():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        password="pebkac",
        host="db",
        port="5432"
    )