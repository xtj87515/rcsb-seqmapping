#!/usr/bin/env python3
# Created by Tongji Xing 09/10/2024

# Requires at least 65G of free RAM (if the chunksize is 800,000)

import pandas as pd
import pymongo
import time
import os
import datetime

chunksize = 800000  # process 800,000 rows (out of 492,361,719) in each cycle

# Connect to MongoDB
# client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")   # this is to connect internally
client = pymongo.MongoClient("mongodb://128.6.159.216:27017/")  # to connect from external instances

# db = client["sifts"]
# client.drop_database("sifts")  # drop/delete the database

## List all databases and print the db names
# databases = client.list_databases()
# for database in databases:
#    print(database["name"])


db = client["diamond-seqmapping"]
# A collection is a group of documents
# collection = db["writeMmseqsFullOutToMongoWithChunking"]
collection = db["custom_search_14"]

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
outf_path = os.path.join(parent_dir, "output", "custom_search_14.tsv")
logf_path = os.path.join(parent_dir, "log", "log_writeToMongo.txt")

with open(outf_path) as f:
    current_time = time.time()
    date_time = datetime.datetime.fromtimestamp(current_time)
    formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    with open(logf_path, "a") as output_file:
        output_file.write(f"Start time is: {formatted_time}\n")
    reader = pd.read_csv(
        f,
        sep="\t",
        chunksize=chunksize,
        header=None,
        names=[
            "qseqid",
            "sseqid",
            "pident",
            "length",
            "mismatch",
            "gapopen",
            "qstart",
            "qend",
            "sstart",
            "send",
            "evalue",
            "bitscore",
            "qcovhsp",
            "scovhsp",
            "staxids",
            "sscinames",
            "sskingdoms",
            "skingdoms",
            "sphylums",
        ],
    )
    i = 1
    for chunk in reader:
        start_time = time.time()
        #        collection.insert_many(chunk.to_dict("documents"))

        # Create a list of documents
        documents = []
        for row in chunk.to_dict("records"):
            # Convert staxids to integer and replace N/A with 0
            staxids = row["staxids"]
            if pd.isna(staxids):
                staxids = 0
            else:
                staxids = int(staxids)

            document = {
                "qseqid": row["qseqid"],
                "sseqid": row["sseqid"],
                "pident": row["pident"],
                "length": row["length"],
                "mismatch": row["mismatch"],
                "gapopen": row["gapopen"],
                "qstart": row["qstart"],
                "qend": row["qend"],
                "sstart": row["sstart"],
                "send": row["send"],
                "evalue": row["evalue"],
                "bitscore": row["bitscore"],
                "qcovhsp": row["qcovhsp"],
                "scovhsp": row["scovhsp"],
                "staxids": staxids,  # Use the converted staxids
                "sscinames": row["sscinames"],
                "sskingdoms": row["sskingdoms"],
                "skingdoms": row["skingdoms"],
                "sphylums": row["sphylums"],
            }
            documents.append(document)

        # Insert the documents into MongoDB
        collection.insert_many(documents, ordered=True)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Write the message to an output file
        with open(logf_path, "a") as output_file:
            if i % 30 == 0:
                output_file.write(f"chunk {i}, insert docs time:, {elapsed_time} seconds\n")

        i = i + 1

    current_time = time.time()
    date_time = datetime.datetime.fromtimestamp(current_time)
    formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    with open(logf_path, "a") as output_file:
        output_file.write(f"End of insertaion time is: {formatted_time}\n")


# Create an index on the 'query' and 'target' columns
def create_index_with_timing(collection):
    start_time = time.time()
    collection.create_index([("qseqid", pymongo.ASCENDING), ("sseqid", pymongo.ASCENDING)])
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Write the index creation time to the output file
    with open(logf_path, "a") as output_file:
        output_file.write(f"Index creation time: {elapsed_time} seconds\n")


create_index_with_timing(collection)

"""
# Look up a field in the collection
 collection.find_one({"sseqid":"UniRef90_P02185"})
 collection.find({"pident":98.7})

>> collection.find_one({"sseqid":"UniRef90_P02185"})
{'_id': ObjectId('67586dc2c0fb77ef04213672'), 'qseqid': '101M_1', 'sseqid': 'UniRef90_P02185', 'pident': 98.7, 'length': 154, 'mismatch': 2, 'gapopen': 0, 'qstart': 1, 'qend': 154, 'sstart': 1, 'send': 154, 'evalue': 1.29e-103, 'bitscore': 302.0, 'qcovhsp': 100.0, 'scovhsp': 100.0, 'staxids': 9755.0, 'sscinames': 'Physeter catodon', 'sskingdoms': 'Eukaryota', 'skingdoms': 'Metazoa', 'sphylums': 'Chordata'}


 collection.find_one({"target":"UniRef100_C8ZJK8"})
 collection.find_one({"fident":0.987})  # but this only returned one result

 for document in collection.find({"qseqid":"101M_1"}).limit(5):
    print(document)

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
