import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader

os.makedirs('pdfs', exist_ok=True)

def downloadPdf(url, dest):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest, "wb") as f:
            f.write(response.content)
        return dest
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def pdfToText(filePath):
    try:
        reader = PdfReader(filePath)
        text = "\n".join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        print(f"Failed to extract text from {filePath}: {e}")
        return ""

def processProduct(product):
    documentation = product.get("documentation", [])
    docTranscr = []
    print(f"Doing product ID: {product['id']}")
    for docUrl in documentation:
        if docUrl.lower().endswith(".pdf"):
            pdfName = os.path.join("pdfs", os.path.basename(docUrl))
            downloadedPdf = downloadPdf(docUrl, pdfName)

            if downloadedPdf:
                text = pdfToText(downloadedPdf)
                docTranscr.append(text)
                try:
                    os.remove(downloadedPdf)
                except Exception as e:
                    print(f"Failed to delete {downloadedPdf}: {e}")

    product["docTranscription"] = docTranscr
    product.pop("documentation", None)

    return product

def main():
    with open("data.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    with ThreadPoolExecutor(max_workers=50) as executor:
        processedProduct = list(executor.map(processProduct, products))

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(processedProduct, f, ensure_ascii=False, indent=4)

    print(f"Processing complete")

if __name__ == "__main__":
    main()