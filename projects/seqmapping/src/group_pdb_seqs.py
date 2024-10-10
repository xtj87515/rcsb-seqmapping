#!/usr/bin/env python3
# Created by Tongji Xing 09/10/2024

from Bio import SeqIO
from collections import defaultdict
import pickle
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import os

# Get the working directory of the script location
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

print(parent_dir + "/input/")


def group_identical_sequences(fasta_file):
    sequence_groups = defaultdict(list)
    with open(fasta_file) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            sequence_groups[str(record.seq)].append(record.id)
    return sequence_groups


fasta_file = parent_dir + "/input/pdb_protein_sequence_all.fasta-A"
sequence_groups = group_identical_sequences(fasta_file)

# for sequence, ids in sequence_groups.items():
#    print(f"Sequence: {sequence}")
#    print(f"IDs: {ids}")


# Save sequence_groups to a pickle file
def save_sequence_groups(sequence_groups, filename):
    with open(filename, "wb") as f:
        pickle.dump(sequence_groups, f)


def load_sequence_groups(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


save_sequence_groups(sequence_groups, parent_dir + "/input/pdb_duplicate_seq_groups.pickle")

# sequence_groups = load_sequence_groups("pdb_duplicate_seq_groups.pickle")
# for sequence, ids in sequence_groups.items():
#    if any("4Z35" in id for id in ids):
#        print(f"Sequence: {sequence}")
#        for id in ids:
#            print(f"ID: {id}")


# Build new FASTA file containing only unique seqs from the sequence groups
def generate_unique_fasta(sequence_groups, output_file):
    with open(output_file, "w") as output_handle:
        for sequence, ids in sequence_groups.items():
            record = SeqRecord(Seq(sequence), id=ids[0], description="")
            output_handle.write(f">{record.id}\n{record.seq}\n")  # create a seqeunce line without wrapping
            # SeqIO.write(record, output_handle, "fasta") # this creates seqeunce line with wrapping


generate_unique_fasta(sequence_groups, parent_dir + "/input/pdb_unique_seqs_all.fasta")
