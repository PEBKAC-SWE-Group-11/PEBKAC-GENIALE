#!/bin/bash

ollama serve &

echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done

# scarica il modello di embedding e il LLM
echo "Pulling required models..."
ollama pull nomic-embed-text
ollama run llama3.2:1b
# ollama run llama3.2:3b
# ollama run deepseek-r1:1.5b

until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

python /app/create_table.py
python /app/insert_data.py
python /app/app.py