import json
from embeddinglocal import getEmbedding
def remove_translations(products):
    cleanedProducts = json.loads(json.dumps(products))  # Deep copy of products

    #print the same prodcut from products and from cleanedProducts
    print(products[0])
    print(cleanedProducts[0])

    for prod in cleanedProducts:
        prod['documentation'] = []

    for prod, cleaned in zip(products, cleanedProducts):
        if 'documentation' in prod:  # Check if 'documentation' key exists
            for doc in prod['documentation']:
                docNames = doc.split("/")[-1]
                if not any(lang in docNames for lang in ['FR', 'EN', 'DE', 'ES', 'EL', 'AR']) and docNames[-4:] != '.mp4':
                    cleaned['documentation'].append(doc)

    return cleanedProducts

def extract_links(products):
    links = {}
    for prod in products:
        for doc in prod['documentation']:
            if doc in links:
                if prod['id'] not in links[doc]['ids']:
                    links[doc]['ids'].append(prod['id'])
            else:
                links[doc] = {'link': doc, 'ids': [prod['id']]}

    linksList = list(links.values())
    return linksList

def process_products(products):
    processed_products = []
    etim_data = {}

        # filepath: /Users/derekgusatto/Documents/Git/PEBKAC-GENIALE/3 - PB/mvp-src/data_processing/products_elaboration.py
    for item in products:
        if 'id' not in item:
            raise KeyError(f"Missing 'id' in product: {item}")
        print(f"Processing product {item['id']}")
        productInfo = f"{item['id']} {item['title']}"
        productInfoVector = getEmbedding(productInfo)
        productDescr = f"{item['id']} {item['title']}"
        productDescrVector = getEmbedding(productDescr)
        
        processed_products.append({
            "product_id": item.get("id", "UNKNOWN_ID"),
            "title": item.get("title", "UNKNOWN_TITLE"),
            "description": item.get("description", ""),
            "etim": None,  
            "id_vector": getEmbedding(item["id"]),
            "idtitle_vector": productInfoVector,
            "idtitledescr_vector": productDescrVector
        })

        technical_data = item['technical_data']
        technical_data['price'] = item['price']
        
        # Convert technicalData dictionary to a text string
        technical_data_text = ', '.join(f"{key}: {value}" for key, value in technical_data.items())
        technical_data_text = f"id: {item['id']}, {technical_data_text}"
        etim_data[item['id']] = technical_data_text

    # Update etim field in processed_products
    for product in processed_products:
        product_id = product["product_id"]
        product["etim"] = etim_data.get(product_id, "")

    return processed_products

# Example usage:
# with open('jsons/data.json', 'r', encoding='utf-8') as f:
#     products = json.load(f)
# processed_products = process_products(products)
# with open('jsons/processed_products.json', 'w') as f:
#     json.dump(processed_products, f, indent=1, ensure_ascii=False)