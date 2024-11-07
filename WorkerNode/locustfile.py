import time
import datetime
from locust import User, task, constant, tag
import pymongo
from time import perf_counter
import bson
from bson import json_util
from bson.json_util import loads
from bson import ObjectId
import os
import string
import random
import pickle
import sys

class Mongouser(User):
    client = pymongo.MongoClient(os.environ['MDBCONNSTRING'])
    db = client["vectest"]
    col = db["data"]

    queryCol = db["queries"]
    allQueries = list(queryCol.aggregate([{"$sample": {"size": 50}}]))

    envlimit = int(os.environ['VSLIMIT'])
    candidates = int(os.environ['VSNUMCANDIDATES'])

    @tag('uc_vecsearch')
    @task(1)
    def uc_vecsearch(self):
        random_query = random.choice(self.allQueries)
        if(random.random() > 0.5):
            vec = random_query["embedding_syn"]
        else:
            vec = random_query["embedding_orig"]
        
        with self.environment.events.request.measure("pymongo", "uc_vecsearch") as request_meta:
            result = self.col.aggregate([{"$vectorSearch": {"queryVector": vec, "path": "embedding", "limit": self.envlimit, "index":"nomic", "numCandidates":self.candidates}}])