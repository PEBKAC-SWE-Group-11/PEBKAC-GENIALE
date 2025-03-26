import json
import logging
import psycopg2
from embeddingLocal import getEmbedding
from connectionDB import getDBConnection
import re
from typing import Any
from psycopg2.extensions import connection as pgConnection
import productsElaboration
from chunkElabotation import processLinksToChunks

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insertChunksFromLinks(cursor: Any, links: list) -> None:
    """
    Processa i link forniti, genera i chunk e li inserisce nel database.
    Args:
        cursor: cursore del database
        links: lista di link a documenti da elaborare
    """
    try:
        logger.info(f"Trovati {len(links)} link da processare.")
        
        #links = links[:1]  # Limita il numero di link per testare il codice
        chunks = processLinksToChunks(links)
        logger.info(f"Generati {len(chunks)} chunk da inserire nel database.")
        
        # Inserisce i chunk nel database
        for i, chunk in enumerate(chunks, 1):
            print(f"Inserimento chunk {i}/{len(chunks)}: {chunk['chunk'][:30]}...")
            cursor.execute("""
                INSERT INTO Chunk (filename, chunk, embedding)
                VALUES (%s, %s, %s)
                ON CONFLICT (filename, chunk) DO NOTHING;
            """, (
                chunk.get('filename', 'unknown'),
                chunk['chunk'],
                chunk['vector']
            ))
        
        logger.info("Tutti i chunk sono stati inseriti con successo nel database.")
    
    except Exception as e:
        logger.info(f"Errore durante l'inserimento dei chunk: {e}")
        raise

def insertProductsFromFile(cursor: Any, products: list) -> None:
    """
    Inserisce i prodotti nel database
    Args:
        cursor: cursore del database
        products: lista di prodotti da inserire
    """
    try:
        cleanedProducts = productsElaboration.removeTranslations(products)
        links = productsElaboration.extractLinks(cleanedProducts)
        processedProducts = productsElaboration.processProducts(cleanedProducts)
        logger.info(f"Trovati {len(processedProducts)} prodotti da inserire")
        
        for i, product in enumerate(processedProducts, 1):
            logger.info(f"Elaborazione prodotto {i}/{len(processedProducts)}")
            cursor.execute("""
                INSERT INTO Product (id, title, description, etim, idVector, idTitleVector, idTitleDescrVector)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                product['productId'],
                product['title'],
                product['description'],
                product['etim'],
                product['idVector'],
                product['idTitleVector'],
                product['idTitleDescrVector']
            ))
        
        logger.info("Tutti i prodotti sono stati inseriti con successo nel database.")

        linksList = list(links.values())
        insertChunksFromLinks(cursor, linksList)
        insertDocumentsFromLinks(cursor, links)
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei prodotti: {e}", exc_info=True)
        raise

def insertDocumentsFromLinks(cursor: Any, links: dict) -> None:
    """
    Inserisce i documenti nel database
    Args:
        cursor: cursore del database
        links: lista di link a documenti da inserire
    """
    try:
        totalLinks = len(links)
        logger.info(f"Trovati {totalLinks} documenti da inserire")
        for i, value in enumerate(links.values(), 1):
            logger.info(f"Salvataggio documento {i}/{totalLinks}")
            doc = re.search(r'(?<=DOCUMENT/)(.*)(?=\.)', value.get('link')).group(0)
            for productId in value['ids']:
                cursor.execute("""
                    INSERT INTO Document (title, productId)
                    VALUES (%s, %s)
                    ON CONFLICT (title, productId) DO NOTHING;
                """, (
                    doc,
                    productId
                ))
        
        logger.info("Tutti i documenti sono stati inseriti con successo nel database.")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei documenti: {e}", exc_info=True)
        raise

def writeProductsInDb(productsFile: str, connection: pgConnection) -> None:
    """
    Inserisce i prodotti nel database usando una connessione esistente
    Args:
        productsFile: percorso al file JSON contenente i prodotti 
        connection: connessione al database
    """
    cursor = None
    try:
        # Disabilita autocommit per la transazione
        connection.autocommit = False
        cursor = connection.cursor()
        
        logger.info("Inizio transazione")
        logger.info(f"Lettura del file {productsFile}")
        
        with open(productsFile, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Inserimento prodotti
        insertProductsFromFile(cursor, products)

        # Commit della transazione
        connection.commit()
        logger.info("Transazione completata con successo")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei dati: {e}", exc_info=True)
        logger.info("Esecuzione rollback della transazione")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.autocommit = True

if __name__ == "__main__":
    try:
        logger.info("Inizio programma di elaborazione dati dataSaving.py")
        connection = getDBConnection()
        writeProductsInDb('jsonData/data.json', connection)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del programma: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Connessione al database chiusa")