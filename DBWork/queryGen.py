import openai
import csv
import pymongo
import time
import random
from nltk.corpus import wordnet
from bson.binary import Binary, BinaryVectorDtype

def generate_bson_vector(vector, vector_dtype):
   return Binary.from_vector(vector, vector_dtype)


fwapikey = "fw_3Zma6AdRJtuThX1NTXpkD9hV"
fwmodel = "nomic-ai/nomic-embed-text-v1.5"
connstr = "mongodb+srv://vscode:fMgiQKiPKJWVrfQ7NZnd@hulu-poc.gtg1b.mongodb.net/?retryWrites=true&w=majority&appName=Hulu-POC&readPreference=nearest"

client = pymongo.MongoClient(connstr)
db = client["scratch"]
srccol = db["data"]
dstcol = db["queries"]

client = openai.OpenAI(
    base_url = "https://api.fireworks.ai/inference/v1",
    api_key=fwapikey,
)

# grab 50 random docs
docs = list(srccol.aggregate([{"$sample": {"size": 50}}]))

for doc in docs:
    # grab description field, grab a subset of words from it
    # and find synonyms for each word
    desc = doc["description"]
    words = desc.split()

    # get a random 5 words from the description
    howManyWords = len(words) 
    if howManyWords <= 6:
        sentence = desc
    else:
        # get random number between 0 and legnth of words
        randomNum = random.randint(0, howManyWords)
        slc = slice(randomNum, randomNum + 5)
        sentence =  " ".join(words[slc])
    
    # now we have a phrase, see if we can sub any synonyms in there
    subPhraseWords = sentence.split()
    maxTries = 5
    currTries = 0
    while currTries <= maxTries:
        if len(subPhraseWords) == 0:
            break
        # get random item from subPhraseWords
        index = random.randint(0, len(subPhraseWords) -1)
        randomItem = subPhraseWords[index]
        s = wordnet.synonyms(randomItem)
        if len(s) > 0:
            if isinstance(s[0], list):
                if len(s[0]) > 0:
                    subPhraseWords[index] = s[0][0].replace("_", " ")
            else:
                subPhraseWords[index] = s[0].replace("_", " ")
        currTries += 1
    newSentence = " ".join(subPhraseWords)

    if len(subPhraseWords) == 0:
        break

    doc = {}
    doc["model"] = fwmodel
    doc["description"] = desc
    doc["search_orig"] = sentence
    doc["search_syn"] = newSentence

    oresp = client.embeddings.create(
        model=fwmodel,
        dimensions=64,
        input=doc["search_orig"]
    )
    doc["embedding_orig"] = generate_bson_vector(oresp.data[0].embedding, BinaryVectorDtype.FLOAT32)

    sresp = client.embeddings.create(
        model=fwmodel,
        dimensions=64,
        input=doc["search_orig"]
    )
    doc["embedding_syn"] = generate_bson_vector(sresp.data[0].embedding, BinaryVectorDtype.FLOAT32)
    
    # print(doc)
    dstcol.insert_one(doc)
