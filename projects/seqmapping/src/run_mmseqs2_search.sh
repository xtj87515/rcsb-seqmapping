#!/bin/sh
# Created by Tongji Xing 09/10/2024

script_dir=$(dirname "$0")
parent_dir="$script_dir/.."

sudo mmseqs easy-search $parent_dir/input/pdb_unique_seqs_all.fasta $parent_dir/input/uniref100.fasta $parent_dir/output/pdb_uniref100_6cpu_s5dot7_e10^-3 $parent_dir/tmp/ -a -s 5.7 --split-memory-limit 100G --threads 6 --format-output query,target,fident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,evalue,bits,qcov,tcov,cigar,qaln,taln >& $parent_dir/log/log_1 &
