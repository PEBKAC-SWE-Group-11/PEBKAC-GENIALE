FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    dos2unix \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && apt-get clean

COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./start.sh /start.sh
RUN dos2unix /start.sh && chmod +x /start.sh

EXPOSE 5000

CMD ["/start.sh"]
