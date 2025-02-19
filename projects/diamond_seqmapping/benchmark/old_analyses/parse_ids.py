# Read IDs from not_contained_ids.txt
with open("not_contained_ids.txt") as f:
    not_contained_ids = set(line.strip() for line in f)

# Read IDs from sifts_mapping.tsv
with open("sifts_mapping.tsv") as f:
    sifts_ids = set(line.strip().split("\t")[0] for line in f)

# Find common IDs
common_ids = not_contained_ids.intersection(sifts_ids)

# Find IDs that are only in not_contained_ids.txt
unique_to_not_contained = not_contained_ids.difference(sifts_ids)

# Write common IDs to a file
with open("common_ids.txt", "w") as f:
    for qseqid in common_ids:
        f.write(f"{qseqid}\n")

# Write unique IDs to another file
with open("unique_to_not_contained.txt", "w") as f:
    for qseqid in unique_to_not_contained:
        f.write(f"{qseqid}\n")

# Print results
print(f"Number of common IDs: {len(common_ids)}")
print(f"Number of unique IDs in not_contained_ids.txt: {len(unique_to_not_contained)}")
