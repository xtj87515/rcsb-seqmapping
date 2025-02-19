#!/usr/bin/env python3
# Created by Tongji Xing 09/10/2024

# Requires at least 65G of free RAM

import pandas as pd
import pymongo
import time
import os

chunksize = 800000  # process 800,000 rows (out of 80,000,000) in each cycle

# Connect to MongoDB
# client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")   # this is to connect internally
client = pymongo.MongoClient("mongodb://128.6.159.216:27017/")  # to connect from external instances

# db = client["sifts"]
# client.drop_database("sifts")  # drop/delete the database

## List all databases and print the db names
# databases = client.list_databases()
# for database in databases:
#    print(database["name"])


db = client["seqmapping"]
# A collection is a group of documents
# collection = db["writeMmseqsFullOutToMongoWithChunking"]
collection = db["MmseqsFullOutToMongo_1"]

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
outf_path = os.path.join(parent_dir, "output", "pdb_uniref100_6cpu_s5dot7_e10^-3")
logf_path = os.path.join(parent_dir, "log", "log_writeToMongo.txt")

with open(outf_path) as f:
    reader = pd.read_csv(
        f,
        sep="\t",
        chunksize=chunksize,
        header=None,
        names=[
            "query",
            "target",
            "fident",
            "alnlen",
            "mismatch",
            "gapopen",
            "qstart",
            "qend",
            "tstart",
            "tend",
            "evalue",
            "bits",
            "qcov",
            "tcov",
            "cigar",
            "qaln",
            "taln",
        ],
    )
    i = 1
    for chunk in reader:
        start_time = time.time()
        collection.insert_many(chunk.to_dict("records"))
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Write the message to an output file
        with open(logf_path, "a") as output_file:
            output_file.write(f"chunk {i}, insert docs time:, {elapsed_time} seconds\n")

        i = i + 1


# Create an index on the 'query' and 'target' columns
def create_index_with_timing(collection):
    start_time = time.time()
    collection.create_index([("query", pymongo.ASCENDING), ("target", pymongo.DESCENDING)])
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Write the index creation time to the output file
    with open(logf_path, "a") as output_file:
        output_file.write(f"Index creation time: {elapsed_time} seconds\n")


create_index_with_timing(collection)

"""
# Look up a field in the collection
 collection.find_one({"target":"UniRef100_C8ZJK8"})
 collection.find_one({"fident":0.987})  # but this only returned one result

 for document in collection.find({"query":"3HGQ_1"}):
    print(document)

# Verify the desired index exists and has the correct fields and sorting order
indexes = collection.list_indexes()
for index in indexes:
    print(index)

# Output of above looks like:
# SON([('v', 2), ('key', SON([('_id', 1)])), ('name', '_id_')])
# SON([('v', 2), ('key', SON([('query', 1), ('target', -1)])), ('name', 'query_1_target_-1')])
# _id_ index is a default index created on every collection. query_1_target_-1 index means this is a compound index created on the query and target fields. 1 in ascending order, -1 in descending order.

"""
