import csv


def replace_column_batch(file1, file2, output_file, batch_size=10000):
    """
    Replaces the 15th column in file1 with the corresponding taxid from file2
    based on matching UniRef90 ID (file1 column 2 and file2 column 1), using batch processing.
    """
    # Step 1: Read file2 into a dictionary for fast lookup
    taxid_dict = {}
    with open(file2, newline="", encoding="utf-8") as f2:
        reader = csv.reader(f2, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            uniref90_id, taxid = row
            taxid_dict[uniref90_id] = taxid

    # Step 2: Process file1 in batches and replace the 15th column with taxid
    with open(file1, newline="", encoding="utf-8") as f1, open(output_file, "w", newline="", encoding="utf-8") as out_f:
        reader = csv.reader(f1, delimiter="\t")
        writer = csv.writer(out_f, delimiter="\t")

        # Write header
        header = next(reader)
        writer.writerow(header)

        batch = []
        for row in reader:
            uniref90_id = row[1]  # Get UniRef90 ID (2nd column)
            if uniref90_id in taxid_dict:
                row[14] = taxid_dict[uniref90_id]  # Replace 15th column (index 14) with taxid
            batch.append(row)

            # If batch is full, write it and clear the batch
            if len(batch) >= batch_size:
                writer.writerows(batch)
                batch.clear()

        # Write any remaining rows
        if batch:
            writer.writerows(batch)

    print(f"Processing complete. Output saved to {output_file}")


# Execution
file1 = "custom_search_14.tsv"  # Replace with the actual path to your file1
file2 = "../input/uniref90_taxid_from_xml.tsv"  # Replace with the actual path to your file2
output_file = "custom_search_14_replaced_taxid.tsv"
replace_column_batch(file1, file2, output_file)
