import json
import ollama
from App.Core.Ports.LLMResponsePort import LLMResponsePort

class LLMResponseService(LLMResponsePort):
    def __init__(self, modelName='llama3.1:8b'):
        self.modelName = modelName

    def getLlmResponse(self, conversationPile, question, textsToEmbed, etimToEmbed):
        formattedMessages = []
        for message in conversationPile:
            role = "assistant" if message["sender"] == "assistant" else "user"
            formattedMessages.append({
                "role": role,
                "content": message["content"]
            })

        context = "\n".join([json.dumps(etimToEmbed[key], ensure_ascii=False) for key in etimToEmbed.keys()])
        context += "\n" + "\n".join([text[3] for text in textsToEmbed])
        
        messages = formattedMessages + [
            {"role": "system", "content": f"Usa questo contesto per rispondere: {context}"},
            {"role": "user", "content": f"{question}"}
        ]
        
        print(f"#####MESSAGGI RICEVUTI DAL LLM: {messages}#####")
        try:   
            stream = ollama.chat(model=self.modelName, messages=messages, stream=True)
            response = ""
            for chunk in stream:
                response += chunk["message"]["content"]
            return response
        except Exception as e:
            return "Failed to get response"
