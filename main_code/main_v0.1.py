import gffutils
import re
import pandas as pd
import sqlalchemy as sql
import os
import zipfile
# this is making my table more structured and maintanable, which makes sense
metadata = sql.MetaData()

intron_sequences = sql.Table(
    "intron_sequences", metadata,
    sql.Column("id", sql.String),
    sql.Column("contig", sql.String),
    sql.Column("intron", sql.String),
    sql.Column("beg", sql.Integer),
    sql.Column("end", sql.Integer),
    sql.Column("seq", sql.String),
    sql.Column("ori", sql.String),
    sql.Column("obs", sql.String)
    )
# Function to create an introns file from a GFF file
def make_introns_file(in_file, out_file):
    """
    Creates an output file containing intron information extracted from a GFF file.
    """
    db = gffutils.create_db(in_file, dbfn=":memory:", id_spec=None, verbose=True, merge_strategy="create_unique", force=True)
    with open(out_file, 'w') as fout:
        for intron in db.create_introns("exon"):
            fout.write(str(intron) + "\n")
    return

# Function to create a database and populate it with intron information
def create_database(introns_file):
    """
    Creates an in-memory SQLite database and populates it with intron information.
    """
    engine = sql.create_engine("sqlite+pysqlite:///:memory:", echo=True)
    metadata.create_all(engine)  # Create the table structure in the database using the defined schema
    with open(introns_file, "r") as file:
        with engine.begin() as conn:
            # Create the intron_sequences table
            for intron in file:
                # Parse the intron information and insert it into the database
                fields = intron.strip().split("\t")
                conn.execute(intron_sequences.insert().values(
                    contig=fields[0],
                    intron="intron", #placeholder, later I need it to iterate inside the contig
                    beg=int(fields[3]),
                    end=int(fields[4]),
                    seq="", #Leave empty since it will be updated later
                    ori=fields[6],
                    obs=fields[8]
                ))
    return engine

# Function to preprocess a FASTA file to combine multi-line sequences into a single line per contig
def preprocess_fasta(fasta_file, out_file):
    """
    Preprocesses a FASTA file to ensure each contig's sequence is on a single line.
    """
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
    return out_file

# Function to add sequences from a FASTA file to the database
def add_sequences(engine, fasta_file):
    """
    Updates the database with sequences from the FASTA file.
    """
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
                    stmt = sql.select(intron_sequences.c.contig, intron_sequences.c.beg, intron_sequences.c.end)\
                        .where(intron_sequences.c.contig == contig) # here the last part is going trough the database and fetching the relevant info for the current contig
                    result = conn.execute(stmt)
                    rows = result.fetchall()

                    #now I can iterate through the rows and update the db with the sequences
                    for row in rows:
                        seq_slice = sequence[int(row.beg):int(row.end)]
                        #now I make an update sql statement, store it in a variable so I can execute it later
                        update_stmt = sql.update(intron_sequences)\
                            .where(
                                (intron_sequences.c.contig == contig) & #gets the current contig inside the db
                                (intron_sequences.c.beg == row.beg) & #gets the same beg value in the contig in the db
                                (intron_sequences.c.end == row.end) #finally matches the end, that way everything is matched
                            )\
                            .values(seq=seq_slice)  # gives the seq_slice variable to update seq in the db
                        conn.execute(update_stmt)  # Execute the update statement

                        # I need to check if the update was succesfull
                        check_stmt = sql.select(intron_sequences.c.seq)\
                            .where(
                                (intron_sequences.c.contig == contig) &
                                (intron_sequences.c.beg == row.beg) &
                                (intron_sequences.c.end == row.end) 
                            )
                        updated_row = conn.execute(check_stmt).fetchone()
                        print(f"{contig} updated with sequence: {updated_row.seq}")
    return engine

# Function to write FASTA files into a ZIP archive
def write_fastas_zip(engine, out_dir_name):
    """
    Writes FASTA files for each intron in the database into a ZIP archive.
    """
    with zipfile.ZipFile(out_dir_name + ".zip", mode="w") as archive:
        with engine.connect() as conn:
            print("Executing SELECT query...")
            result_stmt = sql.select(intron_sequences.c.contig, intron_sequences.c.intron, intron_sequences.c.beg, intron_sequences.c.end, intron_sequences.c.seq, intron_sequences.c.ori, intron_sequences.c.obs)
            result = conn.execute(result_stmt)
            rows = result.fetchall()

            #now I iterate through the rows in the result
            for row in rows:  # Iterate over the fetched rows
                # Create a proper FASTA file name
                name = f"{row.contig}_{row.intron}_{row.beg}-{row.end}.fasta"
                
                # Create the FASTA content
                fasta_content = f">{row.contig} {row.intron} {row.beg}-{row.end} {row.ori} {row.obs}\n{row.seq}\n"
                
                # Debug: Print the FASTA content
                print(f"FASTA content for {name}:\n{fasta_content}")
                
                # Write the content to the ZIP archive
                archive.writestr(f"{row.contig}/{name}", fasta_content)
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
                return False
    return True

# Main script
make_introns_file("Dioscorea_dumetorum_contig1.gff", "Dioscorea_dumetorum_contig1_introns.gff")
db = create_database("Dioscorea_dumetorum_contig1_introns.gff")

# Check if the FASTA file needs preprocessing
fasta_file = "Dioscorea_dumetorum_contig1.fasta"
preprocessed_fasta = "Dioscorea_dumetorum_contig1_preprocessed.fasta"
if not is_fasta_preprocessed(fasta_file):
    print(f"Preprocessing FASTA file: {fasta_file}")
    preprocess_fasta(fasta_file, preprocessed_fasta)
    fasta_file = preprocessed_fasta  # Use the preprocessed file

# Add sequences to the database and write FASTA files to a ZIP archive
db = add_sequences(db, fasta_file)
write_fastas_zip(db, "introns")




