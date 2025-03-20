import json
import logging
import psycopg2
from embeddinglocal import getEmbedding
from connection_db import get_db_connection
import re
from typing import Any
from psycopg2.extensions import connection as pg_connection
import products_elaboration
from chunkElabotation import process_links_to_chunks



# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_chunks_from_links(cursor: Any, links: list) -> None:
    """
    Processa i link forniti, genera i chunk e li inserisce nel database.
    Args:
        cursor: cursore del database
        links: lista di link a documenti da elaborare
    """
    try:
        print(f"Trovati {len(links)} link da processare.")

        #links = links[:1]  # Limita il numero di link per testare il codice
        
        chunks = process_links_to_chunks(links)
        print(f"Trovati {len(links)} link da processare.")

        print(f"Generati {len(chunks)} chunk da inserire nel database.")
        
        # Inserisce i chunk nel database
        for i, chunk in enumerate(chunks, 1):
            print(f"Inserimento chunk {i}/{len(chunks)}: {chunk['chunk'][:30]}...")
            print(f" ----> Chunk {i}: {chunk}")

            cursor.execute("""
                INSERT INTO Chunk (filename, chunk, embedding)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                chunk.get('filename', 'unknown'),
                chunk['chunk'],
                chunk['vector']
            ))
        
        print("Tutti i chunk sono stati inseriti con successo nel database.")
    
    except Exception as e:
        print(f"Errore durante l'inserimento dei chunk: {e}")
        raise
    

def insert_products_from_file(cursor: Any, products: list) -> None:
    """
    Inserisce i prodotti nel database
    Args:
        cursor: cursore del database
        products: lista di prodotti da inserire
    """
    try:
        cleanedProducts = products_elaboration.remove_translations(products)
        links = products_elaboration.extract_links(cleanedProducts)
        processedProducts = products_elaboration.process_products(cleanedProducts)
        print(f"---- !! Prodotti elaborati !! ----")
        total_prods = len(processedProducts)
        print(f"Trovati {total_prods} prodotti da inserire")
        
        for i, product in enumerate(processedProducts, 1):
            print(f"---- !! Prodotti in salvataggio !! ----")
            print(f"Elaborazione prodotti {i}/{total_prods}")
            #print(f"Prodotto {i}: {product}")

            cursor.execute(f"""
                INSERT INTO Product (product_id, title, desciption, etim, id_vector, idtitle_vector, idtitledescr_vector)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING;
            """, (
                product['product_id'],
                product['title'],
                product['description'],
                product['etim'],
                product['id_vector'],
                product['idtitle_vector'],
                product['idtitledescr_vector']
            ))
        
        logger.info("Tutti i prodotti sono stati inseriti con successo nel database.")

        linksList = list(links.values())
        insert_chunks_from_links(cursor, linksList)
        #logger.info("Tutti i chunk sono stati inseriti con successo nel database.")

        insert_documents_from_links(cursor, links)

        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei prodotti: {e}", exc_info=True)
        raise

def insert_documents_from_links(cursor: Any, links: dict) -> None:
    """
    Inserisce i documenti nel database
    Args:
        cursor: cursore del database
        links: lista di link a documenti da inserire
    """
    try:
        total_links = len(links)
        print(f"Trovati {total_links} documenti da inserire")
        for i, value in enumerate(links.values(), 1):  # Use enumerate to track the index
            print(f"Saving document {i}/{total_links}")  # Print progress
            doc = re.search(r'(?<=DOCUMENT/)(.*)(?=\.)', value.get('link')).group(0)
            for product_id in value['ids']:
                cursor.execute("""
                    INSERT INTO Document (title, product_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    doc,
                    product_id
                ))
        
        print("Tutti i documenti sono stati inseriti con successo nel database.")
        
    except Exception as e:
        logger.error(f"Errore durante l'inserimento dei documenti: {e}", exc_info=True)
        raise

def write_products_in_DB(products_file: str, connection: pg_connection) -> None:
    """
    Inserisce i prodotti nel database usando una connessione esistente
    Args:
        products_file: percorso al file JSON contenente i prodotti 
        connection: connessione al database
    """
    cursor = None
    try:
        # Disabilita autocommit per la transazione
        connection.autocommit = False
        cursor = connection.cursor()
        
        logger.info("Inizio transazione")
        logger.info(f"Lettura del file chunk {products_file}")
        
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Inserimento chunks
        insert_products_from_file(cursor, products)

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
        logger.info("Inizio programma di elaborazione dati product_saving.py")
        connection = get_db_connection()
        #write_chunks_in_DB('json_data/chunkfile.json', connection)
        write_products_in_DB('json_data/data.json', connection)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del programma: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Connessione al database chiusa")