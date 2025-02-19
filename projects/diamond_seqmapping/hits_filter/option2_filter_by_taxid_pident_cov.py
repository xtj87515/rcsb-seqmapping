import pymongo
import time
import os
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
logf_path = os.path.join(parent_dir, "log", "log_op2_filter_by_taxid_pident_cov.txt")

current_time = time.time()
date_time = datetime.datetime.fromtimestamp(current_time)
formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
with open(logf_path, "a") as output_file:
    output_file.write(f"Start time is: {formatted_time}\n")

# Step 1: Connect to MongoDB
client = pymongo.MongoClient("mongodb://128.6.159.216:27017/")
db = client["diamond-seqmapping"]

# Step 2: Define the aggregation pipeline
pipeline = [
    # Stage 1: Perform a left join with taxid_map on qseqid = rcsb_id
    {"$lookup": {"from": "taxid_map", "localField": "qseqid", "foreignField": "rcsb_id", "as": "taxid_match"}},
    # Stage 2: Unwind the joined array (taxid_match)
    {
        "$unwind": {
            "path": "$taxid_match",
            "preserveNullAndEmptyArrays": True,  # Keep documents without matches
        }
    },
    # Stage 3: Match documents where staxids matches ncbi_taxon_id
    {
        "$match": {
            "$expr": {
                "$and": [
                    {"$eq": ["$staxids", "$taxid_match.ncbi_taxon_id"]},  # staxids == ncbi_taxon_id
                    {"$gt": ["$pident", 95]},  # pident > 95
                    {"$gt": ["$qcovhsp", 80]},  # qcovhsp > 80
                ]
            }
        }
    },
    # Stage 4: Project the fields you want in the output
    {
        "$project": {
            "_id": 1,
            "qseqid": 1,
            "sseqid": 1,
            "pident": 1,
            "length": 1,
            "mismatch": 1,
            "gapopen": 1,
            "qstart": 1,
            "qend": 1,
            "sstart": 1,
            "send": 1,
            "evalue": 1,
            "bitscore": 1,
            "qcovhsp": 1,
            "scovhsp": 1,
            "staxids": 1,
            "sscinames": 1,
            "sskingdoms": 1,
            "skingdoms": 1,
            "sphylums": 1,
            "taxid_match.ncbi_taxon_id": 1,  # Include matched taxid_map fields if needed
            "taxid_match.ncbi_sci_name": 1,
        }
    },
]

# Step 3: Run the aggregation pipeline
custom_search_14 = db["custom_search_14"]
filtered_results = custom_search_14.aggregate(pipeline)

# Step 4: Export the filtered results to a text file
output_file = "filter_out/op2_filtered_output.txt"
with open(output_file, "w") as f:
    for doc in filtered_results:
        f.write(str(doc) + "\n")

print(f"Filtered results have been written to '{output_file}'")

current_time = time.time()
date_time = datetime.datetime.fromtimestamp(current_time)
formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
with open(logf_path, "a") as output_file:
    output_file.write(f"End of time is: {formatted_time}\n")
