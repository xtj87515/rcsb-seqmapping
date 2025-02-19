#!/bin/sh

grep -f random_100_entries.txt /mnt/vdb1/rcsb-seqmapping/projects/diamond_seqmapping/output/custom_search_6.tsv > diamond_custom6_out100.tsv

grep -f random_100_entries.txt /mnt/vdb1/rcsb-seqmapping/projects/seqmapping/output/pdb_uniref100_6cpu_s5dot7_e10^-3_maxseqs5k > mmseqs_maxseqs5k_out100.tsv
