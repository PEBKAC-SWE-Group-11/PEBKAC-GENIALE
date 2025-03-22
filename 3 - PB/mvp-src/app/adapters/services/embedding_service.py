import requests
import logging

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

class EmbeddingService:
    def get_embeddings(self, prompt):
        payload = {
            "model": "mxbai-embed-large",
            "prompt": f"{prompt}"
        }

        response = requests.post(OLLAMA_EMBED_URL, json=payload)

        if response.status_code == 200:
            query_vector = response.json().get("embedding")
            if not query_vector:
                raise ValueError("Failed to generate embedding for the query.")
        else:
            raise Exception(f"Failed to get embedding: {response.status_code} - {response.text}")

        return query_vector