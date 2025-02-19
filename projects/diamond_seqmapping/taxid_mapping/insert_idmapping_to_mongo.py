# Although input file taxid_for_pdbid_filtered.tsv already removed any duplicate rows or empty values for ncbi_taxonomy_id, this file still contains dulpicate "rcsb_id" for any chimeric sequences for both of which source organism our DW have a record for. So when building the taxid_map we have to keep that in mind, otherwise, any duplicate ncbi_taxonomy_id and its associated values will be removed.

###############################################################
# Step1: Load the taxid_for_pdbid_filtered.tsv file (resulted from querying our Data Warehouse by extracting the ncbi ID that was stored in PDB's mmcif files) into a dictionary with lists
import csv

# Read the TSV file and populate the taxid_map dictionary
taxid_map = []

with open("taxid_for_pdbid_filtered.tsv") as file:
    reader = csv.DictReader(file, delimiter="\t")
    for row in reader:
        row["ncbi_taxon_id"] = int(row["ncbi_taxon_id"])  # Convert string to int
        taxid_map.append(row)


## Check the first 5 items in taxid_map
# print(taxid_map[:5])

###############################################################
# Step2: Insert the rcsb-id to ncbi taxon id mapping into MongoDB

import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://128.6.159.216:27017/")
db = client["diamond-seqmapping"]
taxid_collection = db["taxid_map"]

"""
# Insert all fields for each rcsb_id into the MongoDB collection
documents = [
    {
        "rcsb_id": rcsb_id,
        "taxonomy_entries": entries
    }
    for rcsb_id, entries in taxid_map.items()
]

taxid_collection.insert_many(documents)
print(f"Inserted {len(documents)} documents into the taxid_collection.")
"""

taxid_collection.insert_many(taxid_map)
print(f"Inserted {len(taxid_map)} documents into the taxid_collection.")

client.close()
