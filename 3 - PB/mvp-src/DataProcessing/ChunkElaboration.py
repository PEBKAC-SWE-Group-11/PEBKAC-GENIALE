import os
from pypdf import PdfReader
from typing import List
import requests
import logging
from EmbeddingLocal import getEmbedding

CHARS_PER_CHUNK = 500
OVERLAP = 50

# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def createDirectories():
    """
    Crea le directory necessarie per salvare i PDF e i file di testo.
    """
    os.makedirs('pdfs', exist_ok=True)
    os.makedirs('txts', exist_ok=True)
    logger.info("Directory 'pdfs' e 'txts' create o già esistenti.")

def pdfToTxt(pdfPath: str, txtPath: str):
    """
    Converte un file PDF in un file di testo.
    Args:
        pdfPath: Percorso del file PDF.
        txtPath: Percorso del file di testo da creare.
    """
    with open(pdfPath, 'rb') as pf:
        reader = PdfReader(pf)
        with open(txtPath, 'w', encoding='utf-8') as tf:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    tf.write(text)

def downloadPdf(url: str, savePath: str) -> bool:
    """
    Scarica un file PDF da un URL e lo salva nel percorso specificato.
    Args:
        url: URL del PDF da scaricare.
        savePath: Percorso in cui salvare il file PDF.
    Returns:
        True se il download ha avuto successo, False altrimenti.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(savePath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            logger.info(f"PDF scaricato con successo: {savePath}")
            return True
        else:
            logger.error(f"Errore durante il download del PDF da {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Errore durante il download del PDF da {url}: {e}")
        return False

def processPdf(link: str) -> str:
    """
    Scarica un PDF da un link e lo converte in testo.
    Args:
        link: URL del PDF da scaricare.
    Returns:
        Il percorso del file di testo generato o None se il download fallisce.
    """
    print(f"Scaricamento del PDF da {link}")
    pdfName = os.path.join("pdfs", os.path.basename(link))
    downloadedPdf = downloadPdf(link, pdfName)

    if downloadedPdf:
        print(f"PDF scaricato con successo: {downloadedPdf}")
        txtName = os.path.splitext(os.path.basename(pdfName))[0] + '.txt'
        txtPath = os.path.join('txts', txtName)
        pdfToTxt(pdfName, txtPath)
        logger.info(f"PDF convertito in testo: {txtPath}")
        return txtPath
    else:
        logger.error(f"Impossibile scaricare il PDF da {link}")
        return None

def combineSentences(sentences, buffer=1):
    for i in range(len(sentences)):
        start = max(0, i - buffer)
        end = min(len(sentences), i + buffer + 1)
        combinedSentence = ' '.join(sentences[j]['sentence'] for j in range(start, end))
        sentences[i]['combinedSentence'] = combinedSentence
    return sentences

def calculateDistances(sentences):
    distances = []
    for i in range(len(sentences) - 1):
        currentEmbedding = sentences[i]['combinedSentenceEmbedding']
        nextEmbedding = sentences[i + 1]['combinedSentenceEmbedding']
        similarity = cosine_similarity([currentEmbedding], [nextEmbedding])[0][0]
        distance = 1 - similarity
        distances.append(distance)
    return distances

def processSingleLink(linkData: dict) -> list:
    """
    Processa un singolo link, scarica il PDF e converte in testo.
    Args:
        linkData: Dizionario contenente i dati del link.
    Returns:
        Una lista di chunk elaborati o una lista vuota se il processo fallisce.
    """
    link = linkData.get('link')  # Extract the actual link from the dictionary
    if not link:
        logger.error("Link mancante nei dati forniti.")
        return []

    print(f"Processing link: {link}")
    txtPath = processPdf(link)
    if txtPath:
        return processTextToChunks(txtPath)
    return []

def splitIntoChunks(text, charsPerChunk, overlap):
    chunks = []
    for i in range(0, len(text), charsPerChunk):
        start = max(i - overlap, 0)
        end = min(i + charsPerChunk + overlap, len(text))
        chunks.append(text[start:end])
    return chunks

def processLinksToChunks(links: List[dict]) -> List[dict]:
    """
    Processa una lista di link, scarica i PDF, li converte in testo, elabora i chunk e restituisce i chunk pronti per il database.
    Args:
        links: Lista di dizionari contenenti i link a documenti PDF.
    Returns:
        Una lista di dizionari contenenti i chunk e i relativi embedding.
    """
    createDirectories()
    chunksOutput = []

    for link in links:
        result = processSingleLink(link)
        chunksOutput.extend(result)

    return chunksOutput

def processTextToChunks(txtPath: str) -> List[dict]:
    """
    Elabora un file di testo per generare i chunk e i relativi embedding.
    Args:
        txtPath: Percorso del file di testo.
    Returns:
        Una lista di dizionari contenenti i chunk e i relativi embedding.
    """
    chunks = []
    with open(txtPath, 'r', encoding='utf-8') as f:
        text = f.read()
        logger.info(f"Processing text file: {txtPath}")

        chunkedTexts = splitIntoChunks(text, CHARS_PER_CHUNK, OVERLAP)
        for chunk in chunkedTexts:
            vector = getEmbedding(chunk)
            chunks.append({
                "filename": os.path.splitext(os.path.basename(txtPath))[0],
                "chunk": chunk,
                "vector": vector
            })

    return chunks