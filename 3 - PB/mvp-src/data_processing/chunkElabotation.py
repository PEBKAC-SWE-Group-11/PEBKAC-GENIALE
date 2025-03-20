import os
import re
from multiprocessing import Pool
from pypdf import PdfReader
import numpy as np
from typing import List
import requests

from embeddinglocal import getEmbedding


CHARS_PER_CHUNK = 500
OVERLAP = 50

def create_directories():
    """
    Crea le directory necessarie per salvare i PDF e i file di testo.
    """
    os.makedirs('pdfs', exist_ok=True)
    os.makedirs('txts', exist_ok=True)
    print("Directory 'pdfs' e 'txts' create o già esistenti.")

def pdf_to_txt(pdf_path: str, txt_path: str):
    """
    Converte un file PDF in un file di testo.
    Args:
        pdf_path: Percorso del file PDF.
        txt_path: Percorso del file di testo da creare.
    """
    with open(pdf_path, 'rb') as pf:
        reader = PdfReader(pf)
        with open(txt_path, 'w', encoding='utf-8') as tf:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    tf.write(text)

def downloadPdf(url: str, save_path: str) -> bool:
    """
    Scarica un file PDF da un URL e lo salva nel percorso specificato.
    Args:
        url: URL del PDF da scaricare.
        save_path: Percorso in cui salvare il file PDF.
    Returns:
        True se il download ha avuto successo, False altrimenti.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"PDF scaricato con successo: {save_path}")
            return True
        else:
            print(f"Errore durante il download del PDF da {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Errore durante il download del PDF da {url}: {e}")
        return False

def process_pdf(link: str) -> str:
    """
    Scarica un PDF da un link e lo converte in testo.
    Args:
        link: URL del PDF da scaricare.
    Returns:
        Il percorso del file di testo generato o None se il download fallisce.
    """
    print(f"Scaricamento del PDF da {link}")
    pdf_name = os.path.join("pdfs", os.path.basename(link))
    downloaded_pdf = downloadPdf(link, pdf_name)

    if downloaded_pdf:
        print(f"PDF scaricato con successo: {downloaded_pdf}")
        txt_name = os.path.splitext(os.path.basename(pdf_name))[0] + '.txt'
        txt_path = os.path.join('txts', txt_name)
        pdf_to_txt(pdf_name, txt_path)
        print(f"PDF convertito in testo: {txt_path}")
        return txt_path
    else:
        print(f"Impossibile scaricare il PDF da {link}")
        return None

def combineSentences(sentences, buffer=1):
    for i in range(len(sentences)):
        start = max(0, i - buffer)
        end = min(len(sentences), i + buffer + 1)
        combinedSentence = ' '.join(sentences[j]['sentence'] for j in range(start, end))
        sentences[i]['combined_sentence'] = combinedSentence
    return sentences

def calculateDistances(sentences):
    distances = []
    for i in range(len(sentences) - 1):
        currentEmbedding = sentences[i]['combined_sentence_embedding']
        nextEmbedding = sentences[i + 1]['combined_sentence_embedding']
        similarity = cosine_similarity([currentEmbedding], [nextEmbedding])[0][0]
        distance = 1 - similarity
        distances.append(distance)
        # print(f"{i}#################################")
        # print(sentences[i]['sentence'])
        # print("#################################")
        # print(distance)
    return distances

def process_single_link(link_data: dict) -> list:
    """
    Processa un singolo link, scarica il PDF e converte in testo.
    Args:
        link_data: Dizionario contenente i dati del link.
    Returns:
        Una lista di chunk elaborati o una lista vuota se il processo fallisce.
    """
    link = link_data.get('link')  # Extract the actual link from the dictionary
    if not link:
        print("Link mancante nei dati forniti.")
        return []

    print(f"Processing link: {link}")
    txt_path = process_pdf(link)
    if txt_path:
        return process_text_to_chunks(txt_path)
    return []

def splitIntoChunks(text, chars_per_chunk, overlap):
    chunks = []
    for i in range(0, len(text), chars_per_chunk):
        start = max(i - overlap, 0)
        end = min(i + chars_per_chunk + overlap, len(text))
        chunks.append(text[start:end])
    return chunks


def process_links_to_chunks(links: List[dict]) -> List[dict]:
    """
    Processa una lista di link, scarica i PDF, li converte in testo, elabora i chunk e restituisce i chunk pronti per il database.
    Args:
        links: Lista di dizionari contenenti i link a documenti PDF.
    Returns:
        Una lista di dizionari contenenti i chunk e i relativi embedding.
    """
    create_directories()
    chunks_output = []

    with Pool(processes=20) as pool:
        results = pool.map(process_single_link, links)

    for result in results:
        chunks_output.extend(result)

    return chunks_output

def process_text_to_chunks(txt_path: str) -> List[dict]:
    """
    Elabora un file di testo per generare i chunk e i relativi embedding.
    Args:
        txt_path: Percorso del file di testo.
    Returns:
        Una lista di dizionari contenenti i chunk e i relativi embedding.
    """
    chunks = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()
        print(f"Processing text file: {txt_path}")

        # Use the splitIntoChunks logic
        chunked_texts = splitIntoChunks(text, CHARS_PER_CHUNK, OVERLAP)
        for chunk in chunked_texts:
            vector = getEmbedding(chunk)
            chunks.append({
                "filename": os.path.splitext(os.path.basename(txt_path))[0],
                "chunk": chunk,
                "vector": vector
            })

    return chunks