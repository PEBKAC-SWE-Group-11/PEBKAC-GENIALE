import json
from EmbeddingLocal import getEmbedding
import logging


# Configura il logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def removeTranslations(products):
    """
    Rimuove le traduzioni dai prodotti.
    Args:
        products: Lista di prodotti.
    Returns:
        Lista di prodotti senza traduzioni.
    """
    cleanedProducts = json.loads(json.dumps(products))  # Deep copy of products
    for prod in cleanedProducts:
        prod['documentation'] = []

    for prod, cleaned in zip(products, cleanedProducts):
        if 'documentation' in prod:  # Check if 'documentation' key exists
            for doc in prod['documentation']:
                docNames = doc.split("/")[-1]
                if not any(lang in docNames for lang in ['FR', 'EN', 'DE', 'ES', 'EL', 'AR']) and docNames.lower().endswith('.pdf'):
                    cleaned['documentation'].append(doc)

    return cleanedProducts

def extractLinks(products):
    """
    Estrae i link dai prodotti.
    Args:
        products: Lista di prodotti.
    Returns:
        Dizionario di link con i relativi ID di prodotto.
    """
    links = {}
    for prod in products:
        for doc in prod['documentation']:
            if doc in links:
                if prod['id'] not in links[doc]['ids']:
                    links[doc]['ids'].append(prod['id'])
            else:
                links[doc] = {'link': doc, 'ids': [prod['id']]}
    
    return links

def processProducts(products):
    """
    Processa i prodotti per generare i dati necessari.
    Args:
        products: Lista di prodotti.
    Returns:
        Lista di prodotti processati.
    """
    processedProducts = []
    etimData = {}

    for item in products:
        if 'id' not in item:
            raise KeyError(f"Missing 'id' in product: {item}")
        logger.info(f"Processing product {item['id']}")
        productInfo = f"{item['id']} {item['title']}"
        productInfoVector = getEmbedding(productInfo)
        productDescr = f"{item['id']} {item['title']}"
        productDescrVector = getEmbedding(productDescr)
        
        processedProducts.append({
            "productId": item.get("id", "UNKNOWN_ID"),
            "title": item.get("title", "UNKNOWN_TITLE"),
            "description": item.get("description", ""),
            "etim": None,  
            "idVector": getEmbedding(item["id"]),
            "idTitleVector": productInfoVector,
            "idTitleDescrVector": productDescrVector
        })

        technicalData = item['technical_data']
        technicalData['price'] = item['price']
        
        # Convert technicalData dictionary to a text string
        technicalDataText = ', '.join(f"{key}: {value}" for key, value in technicalData.items())
        technicalDataText = f"id: {item['id']}, {technicalDataText}"
        etimData[item['id']] = technicalDataText

    # Update etim field in processedProducts
    for product in processedProducts:
        productId = product["productId"]
        product["etim"] = etimData.get(productId, "")

    return processedProducts