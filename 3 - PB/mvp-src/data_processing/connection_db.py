import psycopg2
import logging

# Configura il logging
logging.basicConfig(level=logging.INFO)

try:
    # Configura i parametri di connessione
    connection = psycopg2.connect(
       database="postgres",
        user="postgres",
        password="pebkac",
        host="db",
        port="5432"
    )
    cursor = connection.cursor()

    table_name = "test_table"

    # Crea una tabella di esempio
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,  -- Colonna ID auto incrementante
        name TEXT NOT NULL,     -- Colonna per il nome
        description TEXT,       -- Colonna per una descrizione opzionale
        price REAL,             -- Colonna per il prezzo
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Colonna per la data di creazione
    );
    '''
    cursor.execute(create_table_query)

    # Commit per salvare le modifiche nel database
    connection.commit()

    logging.info(f"Tabella {table_name} creata con successo.")

except Exception as e:
    logging.error(f"Errore durante la connessione o la creazione della tabella: {e}", exc_info=True)
finally:
    if connection:
        cursor.close()
        connection.close()
