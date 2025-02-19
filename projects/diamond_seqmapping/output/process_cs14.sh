#!/usr/bin/bash

# Extract the first two cols
#cut -f1,2 custom_search_14.tsv > custom_search_14_2cols.tsv

# Remove the generic "Uniref90" from the sequence IDs in the 2nd column
#awk -F'\t' '{sub(/^UniRef90_/, "", $2); print $1 "\t" $2}' custom_search_14_2cols.tsv > 2cols_custom_search_14.tsv

# Each qseqid (first column) is grouped with all its corresponding sseqid values (second column) in a comma-separated list
awk '
{
    # Append the sseqid to the list for the current qseqid
    if ($1 in arr) {
        arr[$1] = arr[$1] ", " $2
    } else {
        arr[$1] = $2
    }
}
END {
    # Print all qseqid and their corresponding sseqid lists
    for (qseqid in arr) {
        print qseqid, arr[qseqid]
    }
}
' 2cols_custom_search_14.tsv > sorted_cs14_mapping.txt
