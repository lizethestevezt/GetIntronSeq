import sqlalchemy as sql
from metadata import genes, introns  # Importing the intron_sequences table from metadata.py
import logging
from logger_config import setup_logger
# Setup logger
setup_logger("GetIntronSeq.log")
# This script processes FASTA files to ensure that each contig's sequence is on a single line, and adds sequences to the database.
# It also checks if the FASTA file is already in the correct format before preprocessing.


# Function to preprocess a FASTA file to combine multi-line sequences into a single line per contig.
def preprocess_fasta(fasta_file):
    """
    Preprocesses a FASTA file to ensure each contig's sequence is on a single line.
    """
    out_file = fasta_file.replace(".fasta", "_preprocessed.fasta")
    logging.info(f"Preprocessing FASTA file: {fasta_file}")
    with open(fasta_file, "r") as fasta:
        with open(out_file, "w") as out:
            curr_seq = ""
            for line in fasta:
                line = line.strip("\n")
                if line.startswith(">"):  # New contig
                    if curr_seq:  # Write the previous sequence
                        out.write(curr_seq + "\n")
                    curr_seq = ""  # Reset the sequence
                    out.write(line + "\n")  # Write the contig header
                else:  # Sequence line
                    curr_seq += line.strip("\n")  # Append sequence
            if curr_seq:  # Write the last sequence
                out.write(curr_seq + "\n")
    logging.info(f"FASTA file preprocessed and saved to {out_file}")
    return out_file

def parse_fasta(fasta_file):
    """
    Parses a FASTA file and returns a dictionary of contig names and their sequences.
    """
    logging.info(f"Parsing FASTA file: {fasta_file}")
    sequences = {}
    with open(fasta_file, "r") as fasta:
        contig = None
        sequence = []
        for line in fasta:
            line = line.strip()
            if line.startswith(">"):  # Header line
                if contig:  # Save the previous contig and its sequence
                    sequences[contig] = "".join(sequence)
                contig = line.lstrip(">").strip()  # Extract contig name
                sequence = []  # Reset sequence
            else:
                sequence.append(line)  # Append sequence line
        if contig:  # Save the last contig and its sequence
            sequences[contig] = "".join(sequence)
    logging.info(f"FASTA file parsed successfully: {len(sequences)} contigs found.")
    return sequences

# Function to add sequences from a FASTA file to the database
def add_sequences(engine, fasta_file):
    """
    Updates the database with sequences from the FASTA file.
    Ensures no duplicate sequences are added for the same intron.
    """
    logging.info(f"Adding sequences from FASTA file: {fasta_file}")
    sequences = parse_fasta(fasta_file)  # Parse the FASTA file

    with engine.begin() as conn:
        for contig, sequence in sequences.items():
            # Query the database for genes associated with the current contig
            genes_stmt = sql.select(genes.c.gene).where(genes.c.contig == contig)
            gene_rows = conn.execute(genes_stmt).fetchall()

            for gene_row in gene_rows:
                gene = gene_row.gene

                # Query the database for introns associated with the current gene
                introns_stmt = sql.select(introns.c.gene, introns.c.beg, introns.c.end).where(introns.c.gene == gene)
                introns_rows = conn.execute(introns_stmt).fetchall()

                for intron_row in introns_rows:
                    beg = intron_row.beg
                    end = intron_row.end

                    # Extract the sequence slice for the intron
                    seq_slice = sequence[beg:end]

                    # Check if the sequence already exists in the database
                    existing_entry = conn.execute(
                        sql.select(introns.c.seq).where(
                            (introns.c.gene == gene) &
                            (introns.c.beg == beg) &
                            (introns.c.end == end)
                        )
                    ).fetchone()

                    if existing_entry and existing_entry[0] == seq_slice:
                        logging.warning(f"Duplicate sequence detected for gene {gene}, intron {beg}-{end}. Skipping.")
                        continue

                    # Update the introns table with the sequence
                    update_introns_stmt = sql.update(introns).where(
                        (introns.c.gene == gene) &
                        (introns.c.beg == beg) &
                        (introns.c.end == end)
                    ).values(seq=seq_slice)
                    conn.execute(update_introns_stmt)

    logging.info(f"Sequences added to the database from {fasta_file}")
    return engine

# Function to check if a FASTA file is already preprocessed
def is_fasta_preprocessed(fasta_file):
    """
    Checks if the FASTA file is already in the correct format (one line per sequence).
    """
    with open(fasta_file, "r") as fasta:
        for line in fasta:
            if line.startswith(">"):  # Contig header
                continue
            if len(line.strip().split()) > 1:  # Sequence line has spaces or multiple parts
                logging.info(f"FASTA file {fasta_file} is not preprocessed.")
                return False
    logging.info(f"FASTA file {fasta_file} is already preprocessed.")
    return True

