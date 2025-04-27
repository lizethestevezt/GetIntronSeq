import os
import logging
from main_code.input_processing import make_introns_file
from fasta_processing import preprocess_fasta, is_fasta_preprocessed
from database import create_database, add_sequences
from output import write_fastas_zip
from logger_config import setup_logger
# Setup logger
setup_logger("batch_processing.log")

# This script processes multiple GFF and FASTA files in a specified directory.
def process_batch(input_dir, output_dir):
    """
    Processes multiple GFF and FASTA files in the specified input directory.
    Generates output files in the specified output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate through all files in the input directory
    for file in os.listdir(input_dir):
        if file.endswith(".gff"):
            gff_file = os.path.join(input_dir, file)
            fasta_file = os.path.join(input_dir, file.replace(".gff", ".fasta"))

            if not os.path.exists(fasta_file):
                logging.warning(f"FASTA file for {file} not found. Skipping...")
                continue

            # Generate output file paths
            introns_file = os.path.join(output_dir, file.replace(".gff", "_introns.gff"))
            preprocessed_fasta = os.path.join(output_dir, file.replace(".gff", "_preprocessed.fasta"))
            zip_file = os.path.join(output_dir, "introns.zip")

            # Step 1: Extract introns from GFF
            logging.info(f"Processing GFF file: {gff_file}")
            make_introns_file(gff_file, introns_file)

            # Step 2: Preprocess FASTA file if needed
            if not is_fasta_preprocessed(fasta_file):
                logging.info(f"Preprocessing FASTA file: {fasta_file}")
                preprocess_fasta(fasta_file, preprocessed_fasta)
            else:
                preprocessed_fasta = fasta_file

            # Step 3: Create SQLite database and add sequences
            logging.info(f"Creating database for introns in: {introns_file}")
            engine = create_database(introns_file)
            logging.info(f"Adding sequences from FASTA file: {preprocessed_fasta}")
            add_sequences(engine, preprocessed_fasta)

            # Step 4: Generate FASTA files for introns and store in ZIP
            logging.info(f"Writing intron FASTA files to ZIP: {zip_file}")
            write_fastas_zip(engine, output_dir)

    logging.info("Batch processing completed.")

if __name__ == "__main__":
    input_directory = "input_files"  # Replace with your input directory path
    output_directory = "output_files"  # Replace with your output directory path
    process_batch(input_directory, output_directory)