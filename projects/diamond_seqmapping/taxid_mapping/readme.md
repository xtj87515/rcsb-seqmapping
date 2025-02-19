"queryTaxid.py" generates "taxid_for_pdbid.tsv" (~8min)

"filter_taxid_for_pdbid.py" uses "taxid_for_pdbid.tsv" as an input. It generates two output: "taxid_for_pdbid_filtered.tsv" and "taxid_for_pdbid_filtered_out.tsv" (<1min)

"insert_idmapping_to_mongo.py" uses "taxid_for_pdbid_filtered.tsv" as an input. It generates a collection in a MongoDb database(db = diamond-seqmapping, collection = taxid_map) (<1min)
