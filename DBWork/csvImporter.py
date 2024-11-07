import openai
import csv
import pymongo
import time

fwapikey = ""
fwmodel = "nomic-ai/nomic-embed-text-v1.5"
connstr = "mongodb+srv://"

client = pymongo.MongoClient(connstr)
db = client["scratch"]
col = db["data"]

client = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key=fwapikey,
)

with open('search_ml_semantic_feature_service.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    line_count = 0
    toInsert = []
    for r in reader:
        if line_count > 1:
            response = client.embeddings.create(
                model=fwmodel,
                input=r["description"]
            )
            r["embedding"] = response.data[0].embedding
            r["model"] = fwmodel
            print(r)
            toInsert.append(r)
            if len(toInsert) > 100:
                col.insert_many(toInsert)
                toInsert = []
                print("Inserted 100, sleeping 30")
                time.sleep(30)
        line_count += 1
    if len(toInsert) > 0:
        col.insert_many(toInsert)
