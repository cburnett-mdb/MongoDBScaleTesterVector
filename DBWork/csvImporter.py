import openai
import csv
import pymongo
import time
from bson.binary import Binary, BinaryVectorDtype

def generate_bson_vector(vector, vector_dtype):
   return Binary.from_vector(vector, vector_dtype)

# bson_float32_embeddings.append(generate_bson_vector(f32_emb, BinaryVectorDtype.FLOAT32))

fwapikey = "fw_3Zma6AdRJtuThX1NTXpkD9hV"
fwmodel = "nomic-ai/nomic-embed-text-v1.5"
connstr = "mongodb+srv://vscode:fMgiQKiPKJWVrfQ7NZnd@hulu-poc.gtg1b.mongodb.net/?retryWrites=true&w=majority&appName=Hulu-POC&readPreference=nearest"

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
                dimensions=64,
                input=r["description"]
            )
            r["embedding"] = generate_bson_vector(response.data[0].embedding, BinaryVectorDtype.FLOAT32)
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


