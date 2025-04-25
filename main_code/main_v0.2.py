from gff_processing import make_introns_file
from database import create_database
from fasta_processing import preprocess_fasta, is_fasta_preprocessed, add_sequences
from output import write_fastas_zip


# Main script
make_introns_file("Dioscorea_dumetorum_contig1.gff", "Dioscorea_dumetorum_contig1_introns.gff")
db = create_database("Dioscorea_dumetorum_contig1_introns.gff")

# Check if the FASTA file needs preprocessing
fasta_file = "Dioscorea_dumetorum_contig1.fasta"
preprocessed_fasta = "Dioscorea_dumetorum_contig1_preprocessed.fasta"
if not is_fasta_preprocessed(fasta_file):
    preprocess_fasta(fasta_file, preprocessed_fasta)
    fasta_file = preprocessed_fasta  # Use the preprocessed file

# Add sequences to the database and write FASTA files to a ZIP archive
db = add_sequences(db, fasta_file)
write_fastas_zip(db, "introns")

