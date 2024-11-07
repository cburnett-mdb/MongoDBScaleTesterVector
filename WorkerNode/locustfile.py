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

class Mongouser(User):
    client = pymongo.MongoClient(os.environ['MDBCONNSTRING'])
    db = client["vectest"]
    col = db["data"]

    queryCol = db["queries"]
    allQueries = list(queryCol.aggregate([{"$sample": {"size": 50}}]))

    @tag('uc_vecsearch')
    @task(1)
    def insert_one(self):
        try:
            random_query = random.choice(self.allQueries)
            if(random.random() > 0.5):
                vec = random_query["embedding_syn"]
            else:
                vec = random_query["embedding_orig"]
            
            tic = time.time()
            result = self.col.aggregate([{"$vectorSearch": {"queryVector": vec, "path": "embedding", "limit": 3, "index":"nomic"}}])
            self.environment.events.request_success.fire(request_type="pymongo", name="uc_vecsearch", response_time=(time.time()-tic), response_length=0)

        except KeyboardInterrupt:
            print
            sys.exit(0)
        except Exception as e:
            print(f'{datetime.datetime.now()} - DB-CONNECTION-PROBLEM: '
                f'{str(e)}')
            connect_problem = True