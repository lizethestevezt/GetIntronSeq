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
    out_file = "/data" + fasta_file.replace(".fasta", "_preprocessed.fasta")
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

# Function to add sequences from a FASTA file to the database
def add_sequences(engine, fasta_file):
    """
    Updates the database with sequences from the FASTA file.
    """
    logging.info(f"Adding sequences from FASTA file: {fasta_file}")
    with open(fasta_file, "r") as fasta:
        contig = None  
        sequence = ""  

        with engine.begin() as conn:
            for line in fasta:
                line = line.strip()
                if line.startswith(">"):  # Header line
                    contig = line.lstrip(">").strip()
                    sequence = next(fasta).strip() #This is what I needed, this makes it read the next line in the file although I'm in a for loop and not a while loop
                    # Now I get the relevant intron records
                    genes_stmt = sql.select(genes.c.contig, genes.c.gene)\
                        .where(genes.c.contig == contig) # here the last part is going trough the database and fetching the relevant info for the current contig
                    gene_row = conn.execute(genes_stmt).fetchone()
                    if gene_row: #I go through the introns table to update once I've found the gene, I extract it into a variable and then I can do everything else
                        gene = gene_row.gene
                        introns_stmt = sql.select(introns.c.gene, introns.c.beg, introns.c.end)\
                            .where(introns.c.gene == gene) # here the last part is going trough the database and fetching the relevant info for the current contig
                        genes_result = conn.execute(genes_stmt)
                        introns_result = conn.execute(introns_stmt)
                        # Fetch all rows from the result
                        genes_rows = genes_result.fetchall()
                        introns_rows = introns_result.fetchall()

                        # Now I can iterate through the rows and update the db with the sequences
                        for row in introns_rows:
                            seq_slice = sequence[int(row.beg):int(row.end)]
                            #now I make an update sql statement, store it in a variable so I can execute it later
                            update_introns_stmt = sql.update(introns)\
                                .where(
                                    (introns.c.gene == gene) & #gets the current contig inside the db
                                    (introns.c.beg == row.beg) & #gets the same beg value in the contig in the db
                                    (introns.c.end == row.end) #finally matches the end, that way everything is matched
                                )\
                                .values(seq=seq_slice)  # gives the seq_slice variable to update seq in the db
                            conn.execute(update_introns_stmt)  # Execute the update statement

                            # I need to check if the update was succesfull
                            check_stmt = sql.select(introns.c.gene)\
                                .where(
                                    (introns.c.gene == gene) &
                                    (introns.c.beg == row.beg) &
                                    (introns.c.end == row.end) 
                                )
                            updated_row = conn.execute(check_stmt).fetchone()
        logging.info(f"Sequences added to the database from {fasta_file}")
    return

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

