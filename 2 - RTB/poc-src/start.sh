#!/bin/bash

# Function to retry a command up to a specified number of times
#retry() {
#  local n=1
#  local max=5
#  local delay=5
#  while true; do
#     "$@" && break || {
#       if [[ $n -lt $max ]]; then
#         ((n++))
#         echo "Command failed. Attempt $n/$max:"
#         sleep $delay;
#       else
#         echo "The command has failed after $n attempts."
#         return 1
#       fi
#     }
#   done
# }

# avvia ollama server e aspetta che si attivi
#retry ollama serve &
ollama serve &

echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done

# scarica il modello di embedding e il LLM
echo "Pulling required models..."
retry ollama pull nomic-embed-text
retry ollama run llama3.2:1b # e' davvero scarso
# retry ollama run llama3.2:3b # e anche lui non scherza

until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

python /app/create_table.py
python /app/insert_data.py
python /app/app.py