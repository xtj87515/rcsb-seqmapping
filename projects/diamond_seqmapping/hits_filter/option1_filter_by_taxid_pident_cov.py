import pymongo
import time
import os
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
logf_path = os.path.join(parent_dir, "log", "log_op1_filter_by_taxid_pident_cov.txt")

current_time = time.time()
date_time = datetime.datetime.fromtimestamp(current_time)
formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
with open(logf_path, "a") as output_file:
    output_file.write(f"Start time is: {formatted_time}\n")

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://128.6.159.216:27017/")
db = client["diamond-seqmapping"]

# Collections
custom_search_14 = db["custom_search_14"]
taxid_map = db["taxid_map"]

# Step 1: Create a lookup table for taxid_map
taxid_map_lookup = {doc["rcsb_id"]: doc["ncbi_taxon_id"] for doc in taxid_map.find()}

# Step 2: Filter custom_search_14 based on the conditions
filtered_docs = []
for doc in custom_search_14.find():
    rcsb_id = doc["qseqid"]
    staxids = doc["staxids"]
    pident = doc["pident"]
    qcovhsp = doc["qcovhsp"]

    # Check if rcsb_id exists in taxid_map_lookup and staxids matches ncbi_taxon_id
    if rcsb_id in taxid_map_lookup and staxids == taxid_map_lookup[rcsb_id]:
        if pident > 95 and qcovhsp > 80:
            filtered_docs.append(doc)

# Step 3: Export the filtered documents to a text file
with open("filter_out/op1_filtered_output.txt", "w") as f:
    for doc in filtered_docs:
        f.write(str(doc) + "\n")

print("Filtered documents have been written to 'filter_out/op1_filtered_output.txt'")

current_time = time.time()
date_time = datetime.datetime.fromtimestamp(current_time)
formatted_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
with open(logf_path, "a") as output_file:
    output_file.write(f"End of time is: {formatted_time}\n")
