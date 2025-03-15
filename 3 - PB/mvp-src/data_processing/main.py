import logging
import os
import sys
from connection_db import get_db_connection
from create_table import create_tables
from data_saving import write_products_in_DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(connection, json_path):
    """Inizializza il database creando le tabelle necessarie"""
    try:
        create_tables(connection, json_path)
        logger.info("Inizializzazione del database completata con successo")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}")
        raise

def import_data(connection):
    """Importa i dati nel database"""
    try:
        json_path = '/app/data_processing/json_data/staticEmbeddingsByCharacters.json'
        logger.info(f"Tentativo di importazione dati da: {json_path}")
        write_products_in_DB(json_path, connection)
    except Exception as e:
        logger.error(f"Errore durante l'importazione dei dati: {e}")
        raise

def main():
    """Funzione principale"""
    connection = None
    try:
        json_path = '/app/data_processing/json_data/staticEmbeddingsByCharacters.json'
        connection = get_db_connection()
        init_db(connection, json_path)
        import_data(connection)
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}")
        raise
    finally:
        if connection:
            connection.close()
            logger.info("Connessione al database chiusa")

if __name__ == "__main__":
    main()