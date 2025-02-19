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
pipeline = [{"$project": {"_id": 0, "rcsb_polymer_entity_container_identifiers.auth_asym_ids": 1, "rcsb_id": 1}}]

# Execute the aggregation query
result = collection.aggregate(pipeline)


# Save the rcsb_id and corresponding tax_id in two columns in a tsv file:
start_time = time.time()
with open("auth_asym_ids_for_pdbid.tsv", "w", newline="") as tsv_file:
    writer = csv.writer(tsv_file, delimiter="\t")
    writer.writerow(["rcsb_id", "auth_asym_ids"])  # Write the header
    for doc in result:
        rcsb_id = doc.get("rcsb_id", "")
        auth_asym_ids = doc.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_ids", [])
        # For each polymer entity ID, there can be multiple author IDs, this is to iterate through the results and print all items out
        for item in auth_asym_ids:
            writer.writerow([rcsb_id, item])

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Processing time for write-out: {elapsed_time:.4f} seconds")
