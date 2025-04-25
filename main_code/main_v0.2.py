from gff_processing import make_introns_file
from database import create_database
from fasta_processing import preprocess_fasta, is_fasta_preprocessed, add_sequences
from output import write_fastas_zip


# Main script
introns_file = make_introns_file("data/Dioscorea_dumetorum_v1.0.gff")
db = create_database(introns_file)

# Check if the FASTA file needs preprocessing
fasta_file = "data/Dioscorea_dumetorum_v1.0.fasta"
if not is_fasta_preprocessed(fasta_file):
    fasta_file = preprocess_fasta(fasta_file)  # Use the preprocessed file

# Add sequences to the database and write FASTA files to a ZIP archive
db = add_sequences(db, fasta_file)
write_fastas_zip(db, "introns")

