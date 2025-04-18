import psycopg2
import psycopg2.extras
import json
from sklearn.metrics.pairwise import cosine_similarity
import logging
import ollama
from App.Infrastructure.Config.DBConfig import getDatabaseConnection
from App.Core.Ports.ContextExtractorPort import ContextExtractorPort

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0
TOP_PRODUCTS_LIMIT = 20
TOP_SIMILAR_CHUNKS = 3
TOP_PRODUCTS_FINAL = 5
EMBEDDING_MODEL = 'mxbai-embed-large'

class ContextExtractorService(ContextExtractorPort):
    def __init__(self):
        self.dbConnection = getDatabaseConnection()
        self.chunks = self.loadChunks()
    
    def processUserInput(self, userInput):
        userEmbeddings = self.getEmbedding(userInput)

        auxJsons = self.getStructuredProducts()
        totalSimilarProducts = []
        for prodList in auxJsons:
            similarProducts = self.findTopNSimilarProducts(prodList, userEmbeddings, n=TOP_PRODUCTS_LIMIT)
            print("#####similarProducts: ", similarProducts)
            totalSimilarProducts.append(similarProducts)

        processedSimilarProducts = self.aggregateSimilarities(totalSimilarProducts)
        processedSimilarProducts = sorted(processedSimilarProducts.items(), key=lambda x: x[1], reverse=True)
        processedSimilarProducts = dict(processedSimilarProducts[:TOP_PRODUCTS_FINAL])
        
        selectedChunksEmbeddings = self.selectChunksEmbeddings(self.chunks, processedSimilarProducts)
        textsToEmbed = self.findTopNSimilar(selectedChunksEmbeddings, userEmbeddings, n=TOP_SIMILAR_CHUNKS)
        etim = self.extractEtim()
        etimToEmbed = self.selectEtim(etim, textsToEmbed)

        return textsToEmbed, etimToEmbed

    def getStructuredProducts(self):
        query = """
            SELECT id, title, description, idVector, idTitleVector, idTitleDescrVector 
            FROM Product
        """
        
        with self.dbConnection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query)
            products = cursor.fetchall()

        idList = []
        idTitleList = []
        idTitleDescList = []

        for product in products:
            try:
                productId = str(product['id'])
                title = product['title']
                description = product['description']
                
                def parseVector(vectorStr):
                    if not vectorStr:
                        return []
                    try:
                        return json.loads(vectorStr)
                    except (json.JSONDecodeError, TypeError):
                        return []

                idVector = parseVector(str(product['idvector']))
                idTitleVector = parseVector(str(product['idtitlevector']))
                idTitleDescrVector = parseVector(str(product['idtitledescrvector']))
                
                idList.append({
                    "id": productId,
                    "info": productId,
                    "vector": idVector
                })

                idTitleList.append({
                    "id": productId,
                    "info": f"{productId} {title}",
                    "vector": idTitleVector
                })

                idTitleDescList.append({
                    "id": productId,
                    "info": f"{productId} {title} {description}",
                    "vector": idTitleDescrVector
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        return [idList, idTitleList, idTitleDescList]

    def loadChunks(self):
        with self.dbConnection.cursor() as cursor:
            cursor.execute("SELECT id, filename, chunk, embedding FROM chunk")
            rows = cursor.fetchall()
            return [{
                "id": row[0],
                "filename": row[1],
                "chunk": row[2],
                "embedding": json.loads(row[3])
            } for row in rows]

    def extractEtim(self):
        with self.dbConnection.cursor() as cursor:
            cursor.execute("SELECT id, etim FROM Product")
            return {row[0]: row[1] for row in cursor.fetchall()}

    @staticmethod
    def getEmbedding(prompt):
        try:
            return ollama.embeddings(model=EMBEDDING_MODEL, prompt=prompt)['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise ValueError("Failed to generate embedding for the query.")

    @staticmethod
    def findTopNSimilar(chunksEmbeddings, userEmbeddings, n=TOP_SIMILAR_CHUNKS):
        similarities = []
        for item in chunksEmbeddings:
            similarity = cosine_similarity([userEmbeddings], [item['vector']])[0][0]
            similarities.append((item['filename'], similarity, item['productId'], item['chunk']))
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
    
    @staticmethod
    def findTopNSimilarProducts(products, userEmbeddings, n=TOP_PRODUCTS_LIMIT):
        similarProducts = {}
        for product in products:
            productId = product['id']
            productEmbeddings = product['vector']
            similarity = cosine_similarity([userEmbeddings], [productEmbeddings])[0][0]
            if similarity <= SIMILARITY_THRESHOLD:
                similarProducts[productId] = 0
            else:
                similarProducts[productId] = similarity
        
        similarProducts = sorted(similarProducts.items(), key=lambda x: x[1], reverse=True)
        # return similarProducts[:n]
        #########################################################################
        # strategia di "penalizzazione" dei prodotti in base alla loro posizione#
        #########################################################################
        processedSimilarProducts = {}
        position = 1
        for productId, similarity in similarProducts:
            processedProduct = similarity / position # eventualmente incrementare penalizzazione (position**k)
            processedSimilarProducts[productId] = processedProduct
            position += 1
        return dict(list(processedSimilarProducts.items())[:n])
    
    @staticmethod
    def aggregateSimilarities(similaritiesList):
        aggregated = {}
        for similarities in similaritiesList:
            for productId, similarity in similarities.items():
                if productId not in aggregated:
                    aggregated[productId] = 0
                aggregated[productId] += similarity
        return aggregated

    def getDocumentsByProductId(self, productId):
        with self.dbConnection.cursor() as cursor:
            cursor.execute("""
                SELECT d.productId, d.title, p.title as productTitle
                FROM document d
                LEFT JOIN product p ON d.productId = p.id
                WHERE d.productId = %s
            """, (productId,))
            return [{
                'prodId': row[0],
                'doc': row[1],
                'titleProd': row[2]
            } for row in cursor.fetchall()]

    def selectChunksEmbeddings(self, chunksEmbeddings, processedSimilarProducts):
        selectedChunksEmbeddings = []
        addedChunkIds = []
        for productId in processedSimilarProducts.keys():
            documents = self.getDocumentsByProductId(productId)
            for doc in documents:
                filename = doc['doc']                
                for chunk in chunksEmbeddings:
                    if chunk['filename'] == filename and chunk['id'] not in addedChunkIds:
                        selectedChunksEmbeddings.append({
                            'id': chunk['id'],
                            'filename': filename,
                            'productId': doc['prodId'],
                            'chunk': f"ID prodotto: {doc['prodId']}, Titolo: {doc['titleProd']} " + chunk['chunk'],
                            'vector': chunk['embedding']
                        })
                        addedChunkIds.append(chunk['id'])
        return selectedChunksEmbeddings
    
    @staticmethod
    def selectEtim(etim, textsToEmbed):
        etimToEmbed = {}
        for text in textsToEmbed:
            etimToEmbed[text[2]] = etim[text[2]]
        return etimToEmbed

    def __del__(self):
        if hasattr(self, 'dbConnection'):
            self.dbConnection.close()