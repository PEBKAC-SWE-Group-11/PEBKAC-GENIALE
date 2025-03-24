import json
import ollama

class llmResponseService:
    def __init__(self, modelName='llama3.1:8b'):
        self.modelName = modelName

    def getLlmResponse(self, conversationPile, question, textsToEmbed, etimToEmbed):
        context = "\n".join([json.dumps(etimToEmbed[key], ensure_ascii=False) for key in etimToEmbed.keys()])
        context += "\n" + "\n".join([text[3] for text in textsToEmbed])
        messages = conversationPile + [
            {"role": "system", "content": f"Usa questo contesto per rispondere: {context}"},
            {"role": "user", "content": f"{question}"}
        ]
        try:   
            stream = ollama.chat(model=self.modelName, messages=messages, stream=True)
            response = ""
            for chunk in stream:
                response += chunk["message"]["content"]
            return response
        except Exception as e:
            return "Failed to get response"
