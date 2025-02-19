import csv

# Remove duplicate rows and rows where ncbi_taxonomy_id is empty from the original file.

# Input and output file paths
input_file = "taxid_for_pdbid.tsv"
output_file = "taxid_for_pdbid_filtered.tsv"  # Filtered file (no duplicates, no empty ncbi_taxonomy_id)
filtered_out_file = "taxid_for_pdbid_filtered_out.tsv"  # Filtered-out lines (duplicates and empty ncbi_taxonomy_id)

# Set to track seen rows (for duplicate detection)
seen_rows = set()

# Open the input and output files for reading/writing
with open(input_file) as infile, open(output_file, "w", newline="") as outfile, open(
    filtered_out_file, "w", newline=""
) as filtered_out:
    reader = csv.DictReader(infile, delimiter="\t")
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, delimiter="\t")
    filtered_out_writer = csv.DictWriter(filtered_out, fieldnames=reader.fieldnames, delimiter="\t")

    # Write the headers
    writer.writeheader()
    filtered_out_writer.writeheader()

    # Process each row
    for row in reader:
        rcsb_id = row["rcsb_id"]
        ncbi_taxon_id = row["ncbi_taxon_id"]
        ncbi_sci_name = row["ncbi_sci_name"]
        ncbi_parent_sci_name = row["ncbi_parent_sci_name"]

        # Create a unique key for the row (to detect duplicates)
        row_key = (rcsb_id, ncbi_taxon_id)

        # Check for empty ncbi_taxonomy_id or duplicate rows
        if ncbi_taxon_id == "" or row_key in seen_rows:
            # Write to the filtered-out file
            filtered_out_writer.writerow(row)
        else:
            # Write to the filtered file
            writer.writerow(row)
            # Add the row key to the seen_rows set
            seen_rows.add(row_key)
