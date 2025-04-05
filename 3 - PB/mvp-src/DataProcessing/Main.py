import logging
import os
from DataProcessing.ConnectionDB import getDBConnection
from DataProcessing.CreateTable import createTables
from DataProcessing.DataSaving import writeProductsInDb

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
        logger.info("Inizio importazione dati importData Main.py")
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
        jsonPath = os.path.join(os.path.dirname(__file__), 'JsonData/Data.json') 
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