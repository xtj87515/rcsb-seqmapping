#!/bin/sh
# Created by Tongji Xing 09/10/2024

# Get the current directory this script is in
script_dir=$(dirname "$0")
target_dir="$script_dir/../input/"

sudo curl -o "$target_dir/pdb_protein_sequence_all.fasta-A.gz" http://bl-east.rcsb.org/4-coastal/pdb_protein_sequence_all.fasta-A.gz
sudo curl -o "$target_dir/uniref100.fasta.gz" https://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref100/uniref100.fasta.gz

sudo gzip -d "$target_dir/pdb_protein_sequence_all.fasta-A.gz"
sudo gzip -d "$target_dir/uniref100.fasta.gz"

# pdb_protein_sequence_all.fasta-A contains 879,952 lines = 439,976 sequences, many of which are duplicates.
# Therefore, it is necessary to group identical sequences using hash
# First, install essential Python packages (from Bio import SeqIO for handling FASTA files, and from collections import defaultdict for grouping)
sudo pip3 install Bio
sudo python3 group_pdb_seqs.py
