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
from bson.binary import Binary, BinaryVectorDtype
import logging

CONN_STRING = os.environ['MDBCONNSTRING'];
DB_NAME = os.environ['DB_NAME'];
COL_NAME = os.environ['COL_NAME'];
INDEX_NAME = os.environ['INDEX_NAME'];
SEARCH_PATH = os.environ['SEARCH_PATH'];
LIMIT = int(os.environ['LIMIT']);
NUMCANDIDATES = int(os.environ['NUMCANDIDATES']);
FILTER_FLAG = int(os.environ['FILTER_FLAG']);
EXACT_FLAG = int(os.environ['EXACT_FLAG']);

def generate_bson_vector(vector, vector_dtype):
   return Binary.from_vector(vector, vector_dtype)

class Mongouser(User):
    client = pymongo.MongoClient(CONN_STRING)
    db = client[DB_NAME]
    col = db[COL_NAME]

    # Uncomment if you want to use predefined queries
    # queryCol = db["queries"]
    # allQueries = list(queryCol.aggregate([{"$sample": {"size": 50}}]))
    # print(allQueries)

    LOGGED_FIRST_ATTEMPT = False

    @tag('uc_vecsearch')
    @task(1)
    def uc_vecsearch(self):
        # Uncomment if you want to use predefined queries
        # random_query = random.choice(self.allQueries)
        # if(random.random() > 0.5):
        #     vec = random_query["embedding_syn"]
        # else:
        #     vec = random_query["embedding_orig"]
        
        
        # generate a 64 dimension vector, with values between -1 and 1, at random
        vec = [random.uniform(-1, 1) for i in range(64)]
        vec = generate_bson_vector(vec, BinaryVectorDtype.FLOAT32)

        # randomly select a string from either "movie" or "series"
        type = random.choice(["movie", "series", "episode", "sports_team", "sports_event"])
        
        with self.environment.events.request.measure("pymongo", "uc_vecsearch") as request_meta:

            vec_stage = {
                "index": INDEX_NAME,
                "path": SEARCH_PATH, 
                "limit": LIMIT, 
                "numCandidates": NUMCANDIDATES
            };

            if FILTER_FLAG != 0:
                vec_stage["filter"] = {"entity_type": type}

            if EXACT_FLAG == 0:
                vec_stage["exact"] = False
            elif EXACT_FLAG == 1:
                vec_stage["exact"] = True
                del vec_stage["numCandidates"]
            # if it's -1 then don't do anything (don't explicitly set to False)

            # Set it at the end so when the query gets logged, it's easier to read the other settings
            vec_stage["queryVector"] = vec

            result = self.col.aggregate([
                {
                    "$vectorSearch": vec_stage
                },
                {
                    "$project": {
                        "embedding": 0
                    }
                }
            ]).batch_size(LIMIT + 1)

            if not self.LOGGED_FIRST_ATTEMPT:
                logging.info("**** ENVIRONMENT ****")
                logging.info(f"DB_NAME: {DB_NAME}")
                logging.info(f"COL_NAME: {COL_NAME}")
                logging.info(f"INDEX_NAME: {INDEX_NAME}")
                logging.info(f"SEARCH_PATH: {SEARCH_PATH}")
                logging.info(f"LIMIT: {LIMIT}")
                logging.info(f"NUMCANDIDATES: {NUMCANDIDATES}")
                logging.info(f"FILTER_FLAG: {FILTER_FLAG}")
                logging.info(f"EXACT_FLAG: {EXACT_FLAG}")

                logging.info("**** VECTOR STAGE ****")
                logging.info(vec_stage)

                logging.info("**** FIRST RESULT ****")
                result_list = list(result)
                if len(result_list) > 0:
                    logging.info(result_list[0])

                logging.info("**** DOC COUNT ****")
                count = len(result_list)
                logging.info(f"Docs returned: {count}")

                logging.info("**** END ****")
                self.LOGGED_FIRST_ATTEMPT = True