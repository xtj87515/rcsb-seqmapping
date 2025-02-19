grep -A 1 -f ../analyses/random_100_entries.txt pdb_unique_seqs_all.fasta | sed '/^--/d'> subset100_pdb_unique_seqs.fasta

# then I manually deleted all the extra 10 entries 4V61_40~49

grep -A 1 -E "5EJV_2|1G1G_2|2PAV_3|4X2O_3|1BZH_2|1K5M_2" pdb_unique_seqs_all.fasta > subset6_pdb_unique_seqs.fasta
