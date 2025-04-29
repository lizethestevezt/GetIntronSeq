import os
import logging
from input_processing import make_introns_file, input_contains_sequences, add_sequences
from file_type_validation import detect_file_format
from fasta_processing import preprocess_fasta, is_fasta_preprocessed
from database import create_database
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

    for file in os.listdir(input_dir):
        if file.endswith(".gff") or file.endswith(".gff3") or file.endswith(".gtf"):
            gff_file = os.path.join(input_dir, file)

            # Step 1: Detect file format
            format_detected = detect_file_format(gff_file)
            if format_detected not in ["GFF", "GFF3", "GTF", "GZIP"]:
                logging.warning(f"Skipping file {file}: format not recognized as GFF, GFF3, or GTF.")
                continue

            fasta_file = os.path.join(input_dir, file.replace(".gff", ".fasta").replace(".gff3", ".fasta").replace(".gtf", ".fasta"))

            # Step 2: Check if the GFF file contains sequences
            if input_contains_sequences(gff_file):
                logging.info(f"File {file} contains embedded sequences. No separate FASTA needed.")
                fasta_needed = False
            else:
                fasta_needed = True

            # Step 3: If needed, verify existence of corresponding FASTA file
            if fasta_needed:
                if not os.path.exists(fasta_file):
                    logging.warning(f"FASTA file for {file} not found.")
                    user_input = input(f"FASTA file for {file} is missing. Please provide the path to the FASTA file: ").strip()
                    if os.path.exists(user_input):
                        fasta_file = user_input
                    else:
                        logging.error(f"Provided FASTA file path {user_input} does not exist. Skipping {file}.")
                        continue

            # Generate output paths
            introns_file = os.path.join(output_dir, file.replace(".gff", "_introns.gff").replace(".gff3", "_introns.gff").replace(".gtf", "_introns.gff").replace(".gz", "_introns.gff"))
            preprocessed_fasta = os.path.join(output_dir, file.replace(".gff", "_preprocessed.fasta").replace(".gff3", "_preprocessed.fasta").replace(".gtf", "_preprocessed.fasta").replace(".gz", "_preprocessed.fasta"))
            zip_file = os.path.join(output_dir, "introns.zip")

            # Step 4: Extract introns
            logging.info(f"Processing GFF file: {gff_file}")
            make_introns_file(gff_file, introns_file)

            # Step 5: Create database
            logging.info(f"Creating database for introns in: {introns_file}")
            engine = create_database(introns_file)

            # Step 6: Add sequences if needed
            if not fasta_needed:
                logging.info(f"Sequences already present in {file}. No FASTA processing needed.")
            else:
                # Preprocess FASTA if necessary
                if not is_fasta_preprocessed(fasta_file):
                    logging.info(f"Preprocessing FASTA file: {fasta_file}")
                    preprocess_fasta(fasta_file, preprocessed_fasta)
                else:
                    preprocessed_fasta = fasta_file

                logging.info(f"Adding sequences from FASTA file: {preprocessed_fasta}")
                add_sequences(engine, preprocessed_fasta)

            # Step 7: Output intron FASTA files to ZIP
            logging.info(f"Writing intron FASTA files to ZIP: {zip_file}")
            write_fastas_zip(engine, output_dir)

    logging.info("Batch processing completed.")

if __name__ == "__main__":
    input_directory = "input_files"  # Replace with your input directory path
    output_directory = "output_files"  # Replace with your output directory path
    process_batch(input_directory, output_directory)