import gffutils
import logging
from logger_config import setup_logger
import os

# Setup logger
setup_logger("GetIntronSeq.log")
# Function to create an introns file from a GFF file
def make_introns_file(in_file):
    """
    Creates an output file containing intron information extracted from a GFF file.
    """
    out_file = os.path.splitext(in_file)[0] + "_introns.gff"    
    logging.info(f"Creating introns file from input: {in_file}")
    db = gffutils.create_db(in_file, dbfn=":memory:", id_spec=None, verbose=True, merge_strategy="create_unique", force=True)
    with open(out_file, 'w') as fout:
        for intron in db.create_introns("exon"):
            fout.write(str(intron) + "\n")
    return out_file

def make_fasta_file(in_file):
    """
    Creates a FASTA file from a GFF file.
    """
    out_file = os.path.splitext(in_file)[0] + "_sequences.fasta"    
    logging.info(f"Creating FASTA file from input: {in_file}")
    with open(in_file, 'r') as fin, open(out_file, 'w') as fout:
        for line in fin:
            if line.startswith("#"):
                if "start gene" in line:
                    gene_name = line.split(" ")[3]
                    fout.write(f">{gene_name}\n")
                elif "coding sequence" in line:
                    seq = line.split("[")[1].strip("]").strip()
                    fout.write(f"{seq}\n")
                else:
                    continue
    return out_file

def input_contains_introns(input_file):
    """
    Checks if the input file contains intron information.
    """
    db = gffutils.create_db(input_file, dbfn=":memory:", id_spec=None, verbose=True, merge_strategy="create_unique", force=True)
    for feature in db.all_features():
        if feature.featuretype == "intron":
            return True
    return False

def input_contains_sequences(input_file):
    """
    Checks if the input file contains sequence information.
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
        if "coding sequence" in lines:
            return True
    return False

