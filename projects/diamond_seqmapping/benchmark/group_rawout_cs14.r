# First I want to find out if all the queries in pdb_unique_seqs_all.fasta have a corresponding tax ID (extracted from DW)
# Also want to see how many chimerics are in the pdb_unique_seqs_all.fasta based on their tax IDs.
# If chimerics, how many source organisms for each of them?

# pdb_unique_seqs_all.fasta contains 160,950 unique sequences (after removing duplicate seqs from all PDB seqs)
# taxid_for_pdbid_filtered.tsv (was extracted from DW) contains 535,264 non-duplicated PDBID-TaxID pairs (however some of the PDB IDs will have the same sequences, that's why there's a larger number here)
library(dplyr)
library(tidyverse)
library(readr)
library(ggplot2)

pdb_unique_ids <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/input/pdb_unique_ids.txt", col_names = F)
colnames(pdb_unique_ids) <- c("rcsb_id")
taxid_for_pdbid <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/taxid_mapping/taxid_for_pdbid_filtered.tsv", col_names = T)

taxid_sum <- pdb_unique_ids %>%
  left_join(taxid_for_pdbid) %>%
  group_by(rcsb_id) %>%
  summarize(source_organism_num = n(), .groups = 'drop') %>%
  mutate(single_source_organism = ifelse(source_organism_num == 1, "yes", "no"))

taxid_count_sum <- taxid_sum %>%
  group_by(source_organism_num) %>%
  summarize(total_rcsb_ids = n(), .groups = 'drop')

# source_organism_num total_rcsb_ids
# 1         159285
# 2           1582
# 3             77
# 4              5
# 5              1
# i.e. this means seqs with multi source organisms= 1582+77+5+1= 1665 among all the unique rcsb_ids
# Note all 160,950 unique PDB ids have at least 1 corresponding tax_id from NCBI

#########################################
# "rawout_vs_sifts.txt" was generated from compare_rawout_with_sifts.py
# It has 4 cols, 1st= rcsb_id, 2nd = "no/contained"- this indicates whether the SIFTS target is contained in the raw output of Diamond
# search result. If not contained, the 3rd prints either the SIFTS hit or NA (if SIFTS mapping doesn't include this qseqid), then the 4th row prints all the Uniref90 hits from the raw Diamond results.
# There are 152,118 unique IDs produced 154,475 rows of data, meaning 160,950-152,118=8832 rcsb IDs didn't produce any hits after Diamond search (potentially short seqs).
# The rawout_vs_sifts, by how it was generated, meaning all 152,118 IDs have produced at least 1 hit by Diamond search, some of them may have not produced a hit by SIFTS.
rawout_vs_sifts <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/rawout_vs_sifts.txt", col_names = F)
colnames(rawout_vs_sifts) <- c("rcsb_id","SIFTShit_contained_in_rawout","SIFTS_hit", "diamond_hits")

# id_occurances refers to:
# for most rcsb_ids (which are not in pairs_found_by_diamond_alone), it is the number of source seqs found by SIFTS (b/c rawout_vs_sifts is joined with sifts_mapping, if it doesn't have multiple hits in sifts data, our diamond results will only has 1 row corresponding to the hit_list)
# for rcsb_ids in pairs_found_by_diamond_alone, id_occurances =1, but this doesn't mean there's only 1 potential hit. These rcsb_ids can also be potential chimeras.
rawout_vs_sifts <- rawout_vs_sifts %>%
  add_count(rcsb_id, name = "id_occurances") %>%
  left_join(taxid_sum[,1:2], by = "rcsb_id") %>% # adding the source_organism_num
  mutate(diff = source_organism_num - id_occurances)

# tmp:
# diff  count
# -3     20
# -2    113
# -1   1985
# 0 151890
# 1    459
# 2      6
# 3      1
# 4      1
# if diff is positive, i.e. source_organism_num > id_occur, meaning
tmp <- rawout_vs_sifts %>%
  group_by(diff) %>%
  summarize(count = n(), .groups = 'drop')

sum1 <- rawout_vs_sifts %>%
  group_by(SIFTShit_contained_in_rawout) %>%
  summarize(count_contained_or_not = n(), .groups = 'drop')
# sum1:
# contained                                           110461
# no                                                   44014
# Among these 154,475 query-match pairs, the matches for 110461 contain the SIFTS hit, which means with appropriate filter we can get the same hit as SIFTS.

# 1st = 152,118 rcsb_ids
# 2nd col = number of source seqs for each unique rcsb_id
rawout_vs_sifts_id_counts <- rawout_vs_sifts %>%
  count(rcsb_id, name = "id_occurances")

# Original sifts_mapping contains 417,042 entries, among these, there are 137,135 pairs corresponding to our current rcsb_id.
# For the SIFTS data that can map to our unique rcsb_ids, 137,135 pairs were mapped by 134,778 rcsb_ids. There are 152,118-134,778 = 17,340 rcsb_ids that were matched by only Diamond, but not sifts. This can be validated in pairs_found_by_diamond_alone.
sifts_mapping <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/old_analyses/sifts_mapping.tsv",col_names = c("rcsb_id","sseqid"))
sifts_mapping_rcsbID_only <- rawout_vs_sifts_id_counts[,1] %>%
  left_join(sifts_mapping, by = "rcsb_id") %>%
  filter(!is.na(sseqid))
sifts_mapping_rcsbID_only_counts <- sifts_mapping_rcsbID_only %>%
  count(rcsb_id, name = "id_occurances_in_sifts")


# 8832 rcsb_ids that doesn't produce any hits in either Diamond search or SIFTS output (likely short seqs).
# e.g. 148L_2, 173D_2, 185D_1, 193D_2, 1A07_2
no_hits_at_all <- pdb_unique_ids %>%
  anti_join(rawout_vs_sifts_id_counts, by = "rcsb_id")

# id_occurances  count
# 1 149903
# 2   2082
# 3    124
# 4      9
# 152,118 (149903+2082+124+9) non-duplicate rcsb_id produced 154,475(149903*1+2082*2+124*3+9*4) query-hit pairs (matched by either Diamond search or SIFTS)
sum2 <- rawout_vs_sifts_id_counts %>%
  count(id_occurances, name = "count")

# 110,461 pairs found by both Diamond and SIFTS, some of these are chimeras
pairs_found_by_both <- rawout_vs_sifts %>%
  filter(SIFTShit_contained_in_rawout == "contained")

# 17,340 pairs found by Diamond only, not SIFTS
pairs_found_by_diamond_alone <- rawout_vs_sifts %>%
  filter(SIFTShit_contained_in_rawout == "no" & is.na(SIFTS_hit))

# 26,674 pairs where the SIFTS hit is not contained in the hit_list of Dimond search
# this can include multiple senarios, further exams are needed.
# possible senario: 1) the SIFT hit uniref ID doesn't exist in our input Uniref,
# 2) might be a chimera seq where Diamond picked up 1 or a few hits but missed others
# 3) check the taxid for both SIFTS_hit and potential Diamond hit, see which one matches better. there are many taxid=NAs when we built our Uniref90 for diamond search
pairs_found_by_sifts_alone <- rawout_vs_sifts %>%
  filter(SIFTShit_contained_in_rawout == "no"& !is.na(SIFTS_hit))

write_tsv(pairs_found_by_sifts_alone, "/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/pairs_found_by_sifts_alone.tsv", col_names = F)


######################################### Closer look at the 26k query-hit pairs
# From here I used 26k_vs_uniref90.py to generate two new files: matches_26k.tsv & non_matches_26k.tsv
# 998 pairs_of_interest_among26k = sifts hit exists in our input uniref90.fasta, 1) if the query is a chimera, it's possible Diamond found 1 of the 2 or few targets. 2) otherwise it's a true missing hit. 3) Diamond found better hits
# 25,676 pairs_alt_hits_among26k = sifts hit DON'T exist in our input uniref90.fasta (maybe due to database update, maybe due to a new name assigned). Do they exist in uniref100.fasta?
pairs_of_interest_among26k <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/matches_26k.tsv", col_names = F)
pairs_alt_hits_among26k <- read_tsv("/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/non_matches_26k.tsv", col_names = F)
colnames(pairs_of_interest_among26k) <- colnames(rawout_vs_sifts)
colnames(pairs_alt_hits_among26k) <- colnames(rawout_vs_sifts)

pairs_alt_hits_among26k <- pairs_alt_hits_among26k %>%
  left_join(rawout_vs_sifts_id_counts, by = "rcsb_id") %>%
  filter(id_occurances>1) %>%






# ??485 rcsb_ids produced 498 true_missing_pairs, where the queries are NOT chimeras & the SIFTS target exist in input Uniref90.fasta, so Diamond just missed these hits (or maybe matched better hits?)
true_missing_pairs <- pairs_of_interest_among26k %>%
  filter(id_occurances==1) %>%
  left_join(taxid_for_pdbid[,1:2], by = "rcsb_id") %>%
  add_count(rcsb_id, name = "rcsb_id_count")

  rename(query_taxid = ncbi_taxon_id)

# 513 pairs (where the query is a chimera), they might have at least 1 target already picked up by Diamond?
# For only 7 of these pairs- Diamond hasn't picked up any of the correct hits, for all others, Diamond has picked up at least 1 other hit.
chimeras_of_interest <- pairs_of_interest_among26k %>%
  left_join(rawout_vs_sifts_id_counts, by = "rcsb_id") %>%
  filter(id_occurances>1) %>%
  add_count(rcsb_id, name = "occurrences_rcsb_id") %>%
  mutate(hits_picked_by_diamond = id_occurances - occurrences_rcsb_id)  # this is the number of hits matched by Diamond for these chimeras

################### Closer look at 485 true_missing_pairs, first get their seq length
library(Biostrings)
pdb_fasta <- "/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/input/pdb_unique_seqs_all.fasta"

# Read the full FASTA file
pdb_seqs <- readAAStringSet(pdb_fasta)

# Create a named vector of sequence lengths
seq_lengths <- setNames(width(pdb_seqs), names(pdb_seqs))

# Add the sequence lengths to the tibble
true_missing_pairs <- true_missing_pairs %>%
  mutate(query_length = seq_lengths[rcsb_id])


##### create a density plot for the seq length distribution for all PDB unique seqs
# Create a tibble for plotting
# Mean of all of the lengths = 27, median = 221
lengths_tibble <- tibble(
  length = width(pdb_seqs)
)

# Create a distribution plot
ggplot(lengths_tibble, aes(x = length)) +
  geom_density(fill = "skyblue", alpha = 0.5) +  # Density plot
  labs(
    title = "Distribution of Sequence Lengths",
    x = "Sequence Length",
    y = "Density"
  ) +
  theme_minimal()

# There are some extreme large lengths, temporarily remove them
# Calculate the 95th percentile of sequence lengths
upper_limit <- quantile(lengths_tibble$length, 0.95)
ggplot(lengths_tibble, aes(x = length)) +
  geom_histogram(binwidth = 10, fill = "skyblue", color = "black") +
  coord_cartesian(xlim = c(0, upper_limit)) +  # Zoom in on the majority of the data
  labs(
    title = "Distribution of Sequence Lengths (Zoomed In)",
    x = "Sequence Length",
    y = "Frequency"
  ) +
  theme_minimal()

ggplot(lengths_tibble, aes(y = length)) +
  geom_boxplot(fill = "skyblue") +
  labs(
    title = "Boxplot of Sequence Lengths",
    y = "Sequence Length"
  ) +
  theme_minimal()

###################


set.seed(123)
true_missing_pairs_sub50 <- true_missing_pairs %>%
  slice_sample(n=50)
# Generate a command line to grep the seqs of these 50 queries from the pdb_unique_seqs_all.fasta file
grep_pattern <- paste(true_missing_pairs_sub50$rcsb_id, collapse = "|")
# grep -A 1 -E "1MHU_1|1GNM_1|7SAP_1|2RQG_1|8Q92_1|1NCP_2|8DHY_1|2EOK_1|3ICI_2|2YTN_1|5WDF_3|2EOP_1|1ODY_1|4R2E_1|4UOW_1|3MN7_2|2RUM_1|1DSV_1|2B1U_1|3CTN_1|8JG5_3|2R5P_1|8J46_1|1DUM_1|5KY0_2|7CEA_2|8I3E_1|2EMB_1|1GL1_2|7L1U_6|6E52_1|2N5E_1|8CKB_2|8C5C_1|2JMF_1|1X6E_1|1GW3_1|2MZ7_1|2EN8_1|2EM9_1|1HEF_1|6MV5_3|7WO0_1|2GWW_2|2EQ1_1|2LW9_1|5EGB_3|2EMA_1|4UOW_2|2ELT_1" pdb_unique_seqs_all.fasta > ../benchmark/true_missing_pairs_sub50_seqs.fasta

pairs_alt_hits_among26k_sub100 <- pairs_alt_hits_among26k %>%
  slice_sample(n=100)
write_tsv(pairs_alt_hits_among26k_sub100, "/mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/benchmark/pairs_alt_hits_among26k_sub100.tsv", col_names = T)
