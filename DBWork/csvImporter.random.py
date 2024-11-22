import random
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
        vec = [random.uniform(-1, 1) for i in range(64)]
        vec = generate_bson_vector(vec, BinaryVectorDtype.FLOAT32)
        r["embedding"] = vec

        toInsert.append(r)
        if len(toInsert) > 10000:
            col.insert_many(toInsert)
            toInsert = []
        # time.sleep(0.1) # sleep 100ms to adhere to 600qpm rate limit for fireworks.ai

    if len(toInsert) > 0:
        col.insert_many(toInsert)



