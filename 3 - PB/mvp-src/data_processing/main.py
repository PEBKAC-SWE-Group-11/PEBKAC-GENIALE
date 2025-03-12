from connection_db import get_db_connection
from create_table import create_tables
# from data_saving import write_products_in_DB  # Commentato temporaneamente
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Inizializza il database creando le tabelle necessarie"""
    connection = None
    try:
        # 1. Stabilisce la connessione
        connection = get_db_connection()
        
        # 2. Crea le tabelle
        create_tables(connection)
        
        logger.info("Inizializzazione del database completata con successo")
        return connection
        
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}", exc_info=True)
        if connection:
            connection.close()
        raise

def main():
    try:
        # Inizializza il database e mantiene la connessione
        connection = initialize_database()
        
        # 3. Inserisce i dati (se necessario)
        # Commentato temporaneamente
        # write_products_in_DB('data/product_file.json', connection)
        
        logger.info("Processo completato con successo")
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}", exc_info=True)
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Connessione al database chiusa")

if __name__ == "__main__":
    main()