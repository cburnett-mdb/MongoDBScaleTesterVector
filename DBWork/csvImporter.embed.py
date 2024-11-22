import openai
import csv
import pymongo
import time
from bson.binary import Binary, BinaryVectorDtype
from tqdm import tqdm

def generate_bson_vector(vector, vector_dtype):
   return Binary.from_vector(vector, vector_dtype)

# bson_float32_embeddings.append(generate_bson_vector(f32_emb, BinaryVectorDtype.FLOAT32))

fwapikey = ""
fwmodel = "nomic-ai/nomic-embed-text-v1.5"
connstr = ""

client = pymongo.MongoClient(connstr)
db = client[""]
col = db[""]

client = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key=fwapikey,
)

with open('catalog.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    line_count = 0
    toInsert = []
    total_lines = sum(1 for row in reader)
    csvfile.seek(0)
    next(reader)  # Skip header row

    for r in tqdm(reader, total=total_lines, desc="Processing rows"):
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
            # print("Inserted 100, sleeping 30")
            # time.sleep(30)
            
    if len(toInsert) > 0:
        col.insert_many(toInsert)


