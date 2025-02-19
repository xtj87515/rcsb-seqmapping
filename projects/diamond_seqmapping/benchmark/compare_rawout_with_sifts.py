# Here's an example of what this script does:
# Input file 1 (sifts_mapping.tsv):
# 6USF_1  P43681
# 6USF_1  P0ABE7
# 8C8Q_8  ABCDEF
#
# Input file 2 (sorted_cs14_mapping.txt):
# 8C8Q_8 Q9P4W1, S9W697, S9PQG4
# 6USF_1 UPI0014612D6F, UPI00187A9975, A0A4X2L9N9, UPI0003F1852C, A0A6P6BKS6, A0A8D1Q7J4, P43681, A0A8C5QFS5
# 7XYZ_9 Q12345, Q67890
#
# Output file (rawout_vs_sifts.txt):
# 8C8Q_8	no	ABCDEF	Q9P4W1, S9W697, S9PQG4
# 6USF_1	contained	P43681
# 6USF_1	no	P0ABE7	UPI0014612D6F, UPI00187A9975, A0A4X2L9N9, UPI0003F1852C, A0A6P6BKS6, A0A8D1Q7J4, P43681, A0A8C5QFS5
# 7XYZ_9	no	NA	Q12345, Q67890

# In output file:
# 1st col = every rcsb_id from sorted_cs14_mapping.txt
# 2nd col = whether the sifts hit(from input 1) is contained in the hit_list (from input 2),
#           if it's not, prints "no". if it is, prints "contained".
# 3rd col = if 2nd col is "contained", this col prints the sifts_hit,
#           if 2nd col is "no", this col either prints the sifts_hit, or if this rcsb_id isn't included in input file 2, prints "NA"
# 4th col = if 2nd col is "no", this col prints the hit_list(from input 2),
#           if 2nd col is "contained", this col is empty.


# Load sifts_mapping.tsv, this file was generated locally on my laptop using "compareWithSIFTS.R"
sifts = {}
with open("sifts_mapping.tsv") as f:
    for line in f:
        parts = line.strip().split("\t")  # sifts_mapping.tsv is tab-separated
        if len(parts) == 2:  # Ensure the line has exactly two columns
            qseqid, sseqid = parts
            if qseqid not in sifts:
                sifts[qseqid] = []  # Initialize a list for each qseqid
            sifts[qseqid].append(sseqid)  # Append sseqid to the list
        else:
            print(f"Skipping malformed line in sifts_mapping.tsv: {line.strip()}")

# Process sorted_cs14_mapping.tsv
with open("../../output/sorted_cs14_mapping.txt") as f_in, open("rawout_vs_sifts.txt", "w") as f_out:
    for line_number, line in enumerate(f_in, 1):
        parts = line.strip().split(" ", 1)  # Split by the first space only
        if len(parts) == 2:  # Ensure the line has exactly two columns
            qseqid, sseqid_list = parts
            sseqid_set = set(sseqid_list.split(", "))  # Convert sseqid_list to a set for faster lookup
            if qseqid in sifts:
                for sseqid in sifts[qseqid]:
                    if sseqid in sseqid_set:
                        # If sseqid is contained, write "contained" and leave the 4th column empty
                        f_out.write(f"{qseqid}\tcontained\t{sseqid}\t\n")
                    else:
                        # If sseqid is not contained, write "no" and include the sseqid_list in the 4th column
                        f_out.write(f"{qseqid}\tno\t{sseqid}\t{sseqid_list}\n")
            else:
                # If qseqid is not in sifts, write "no", fill the 3rd column with "NA", and include the sseqid_list in the 4th column
                f_out.write(f"{qseqid}\tno\tNA\t{sseqid_list}\n")
        else:
            print(f"Skipping malformed line in sorted_cs14_mapping.tsv (line {line_number}): {line.strip()}")
