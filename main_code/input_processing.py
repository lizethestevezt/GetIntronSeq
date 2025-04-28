import gffutils
import logging
from logger_config import setup_logger
from file_type_validation import detect_file_format
from database import create_database, add_sequences
from fasta_processing import preprocess_fasta, is_fasta_preprocessed
from output import write_fastas_zip
import shutil
import os
import gzip

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

#Function to process gzip files
def extract_gzip(input_file, output_dir):
    """
    Extracts a GZIP file into the specified output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    extracted_file_path = os.path.join(output_dir, os.path.basename(input_file).replace(".gz", ""))
    with gzip.open(input_file, 'rb') as f_in:
        with open(extracted_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return extracted_file_path

def process_single_file(input_file, fasta_file, output_name):
    """
    Processes a single GFF file to extract introns and generate output.
    """
    # Detect file format
    format_type = detect_file_format(input_file)
    print(f"Detected file format: {format_type}")

    if format_type == "Unknown":
        raise ValueError("Unsupported file format. Please provide GFF, GFF3, or GTF file.")

    # Check if the input file contains introns
    if not input_contains_introns(input_file):
        print("The input file does not contain introns. Exiting.")
        return

    # Check if the input file contains sequences
    if not input_contains_sequences(input_file):
        if not fasta_file:
            raise ValueError("The input file does not contain sequences. Please provide a FASTA file using the --fasta argument.")
    else:
        # If sequences are present in the input file, use it as the FASTA file
        fasta_file = make_fasta_file(input_file)
        print(f"FASTA file created: {fasta_file}")

    # Process the input file to extract introns
    introns_file = make_introns_file(input_file)

    # Create the database
    db = create_database(introns_file)

    # Check if the FASTA file needs preprocessing
    if not is_fasta_preprocessed(fasta_file):
        fasta_file = preprocess_fasta(fasta_file)  # Use the preprocessed file

    # Add sequences to the database and write FASTA files to a ZIP archive
    db = add_sequences(db, fasta_file)
    write_fastas_zip(db, output_name)

    print(f"Processing of {input_file} completed successfully.")