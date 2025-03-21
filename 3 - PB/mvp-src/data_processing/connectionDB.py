import psycopg2
import logging
import time

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def getDBConnection():
    """Stabilisce la connessione al database"""
    connection = None
    retries = 10
    delay = 5

    connectionParams = {
        "dbname": "postgres",
        "user": "postgres",
        "password": "pebkac",
        "host": "db",
        "port": "5432",
        "connect_timeout": 10,
        "client_encoding": 'UTF8',
        "application_name": 'data_processing'
    }

    for attempt in range(retries):
        try:
            logger.info(f"Tentativo {attempt + 1} di connessione al database...")
            connection = psycopg2.connect(**connectionParams)
            logger.info("Connessione al database stabilita con successo")
            return connection
        except psycopg2.OperationalError as e:
            logger.warning(f"Tentativo {attempt + 1} di {retries} fallito: {str(e)}")
            if attempt < retries - 1:
                logger.info(f"Attendo {delay} secondi prima di riprovare...")
                time.sleep(delay)
            else:
                logger.error("Impossibile connettersi al database dopo tutti i tentativi")
                raise e