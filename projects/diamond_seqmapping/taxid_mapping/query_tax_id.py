import pymongo
import time
import csv

# Connect to MongoDB
client = pymongo.MongoClient(
    "mongodb://updater:w31teQuerie5@128.6.159.213:27017/?connectTimeoutMS=3000000&socketTimeoutMS=3000000"
)

# Select the database and collection
db = client["dw"]
collection = db["core_polymer_entity"]

## Verify the content
# print(client.list_database_names())
# print(db.list_collection_names())


# Define the aggregation pipeline
pipeline = [
    {"$match": {"rcsb_entity_source_organism.provenance_source": "Primary Data"}},
    {
        "$project": {
            "_id": 0,
            "rcsb_entity_source_organism.ncbi_taxonomy_id": 1,
            "rcsb_entity_source_organism.ncbi_scientific_name": 1,
            "rcsb_entity_source_organism.ncbi_parent_scientific_name": 1,
            "rcsb_id": 1,
        }
    },
]

# Execute the aggregation query
result = collection.aggregate(pipeline)


# Save the rcsb_id and corresponding tax_id in two columns in a tsv file:
start_time = time.time()
with open("taxid_for_pdbid.tsv", "w", newline="") as tsv_file:
    writer = csv.writer(tsv_file, delimiter="\t")
    writer.writerow(["rcsb_id", "ncbi_taxon_id", "ncbi_sci_name", "ncbi_parent_sci_name"])  # Write the header
    for doc in result:
        rcsb_id = doc.get("rcsb_id", "")
        rcsb_entity_source_organism = doc.get("rcsb_entity_source_organism", [])
        # For chemric seqs, there can be more than one source organism, this is to iterate through the results and print all items out
        for item in rcsb_entity_source_organism:
            ncbi_taxonomy_id = item.get("ncbi_taxonomy_id", "")
            ncbi_scientific_name = item.get("ncbi_scientific_name", "")
            ncbi_parent_scientific_name = item.get("ncbi_parent_scientific_name", "")
            writer.writerow([rcsb_id, ncbi_taxonomy_id, ncbi_scientific_name, ncbi_parent_scientific_name])

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Processing time for write-out: {elapsed_time:.4f} seconds")
