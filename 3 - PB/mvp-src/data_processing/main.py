import logging
import os
import sys
from data_processing.connectionDB import getDBConnection
from data_processing.createTable import createTables
from data_processing.dataSaving import writeProductsInDb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initDB(connection):
    """Inizializza il database creando le tabelle necessarie"""
    try:
        createTables(connection)
        logger.info("Inizializzazione del database completata con successo")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}")
        raise

def importData(connection, jsonPath):
    """Importa i dati nel database"""
    try:
        logger.info("Inizio importazione dati importData main.py")
        logger.info(f"Tentativo di importazione dati da: {jsonPath}")
        writeProductsInDb(jsonPath, connection)
    except Exception as e:
        logger.error(f"Errore durante l'importazione dei dati: {e}")
        raise

def main():
    """Funzione principale"""
    connection = None
    try:
        connection = getDBConnection()
        initDB(connection)
        jsonPath = os.path.join(os.path.dirname(__file__), 'jsonData/data.json') 
        importData(connection, jsonPath)
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}")
        raise
    finally:
        if connection:
            connection.close()
            logger.info("Connessione al database chiusa")

if __name__ == "__main__":
    main()