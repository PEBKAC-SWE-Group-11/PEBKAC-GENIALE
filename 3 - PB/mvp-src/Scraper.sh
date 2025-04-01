#!/bin/bash

mkdir -p /App/DataProcessing/JsonData
chmod -R 777 /App/DataProcessing/JsonData

echo "Starting Scrapy spider..."
scrapy runspider /App/DataProcessing/Scraper/Scraper/spiders/Scraper.py -O /App/DataProcessing/JsonData/Data.json

if [ -f "/App/DataProcessing/JsonData/NewData.json" ]; then
    echo "Scrapy completed successfully. File created: /App/DataProcessing/JsonData/Data.json"
else
    echo "Scrapy failed or file not created: /App/DataProcessing/JsonData/Data.json"
    exit 1
fi

echo "Running Python script..."
python /App/DataProcessing/Main.py