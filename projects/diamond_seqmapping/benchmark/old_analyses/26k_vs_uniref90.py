# Load IDs from uniref90_ids.tsv
with open("../input/uniref90_ids.tsv") as f:
    uniref90_ids = set(line.strip() for line in f)

# Initialize lists to store matches and non-matches
matches = []
non_matches = []

# Process sifts_mapping_of_interest_26k.tsv
with open("sifts_mapping_of_interest_26k.tsv") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:  # Ensure the line has exactly two columns
            col1, col2 = parts
            if col2 in uniref90_ids:
                matches.append(line.strip())  # Add to matches
            else:
                non_matches.append(line.strip())  # Add to non-matches

# Write matches to a new file
with open("matches_26k.tsv", "w") as f:
    for line in matches:
        f.write(f"{line}\n")

# Write non-matches to a new file
with open("non_matches_26k.tsv", "w") as f:
    for line in non_matches:
        f.write(f"{line}\n")

print(f"Number of matches: {len(matches)}")
print(f"Number of non-matches: {len(non_matches)}")
