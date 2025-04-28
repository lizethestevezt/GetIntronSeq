from input_processing import make_introns_file, input_contains_introns, input_contains_sequences, make_fasta_file
from database import create_database
from fasta_processing import preprocess_fasta, is_fasta_preprocessed, add_sequences
from output import write_fastas_zip
from file_type_validation import detect_file_format
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="GetIntronSeq: Extract intron sequences from genome files.")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input file (GFF, GFF3, or GTF format)."
    )
    parser.add_argument(
        "--fasta",
        required=False,
        help="Path to the corresponding FASTA file (if sequences are not in the input file)."
    )
    parser.add_argument(
        "--output",
        required=False,
        default="introns",
        help="Name of the output directory or ZIP archive (default: 'introns')."
    )
    args = parser.parse_args()

    # Extract arguments
    input_file = args.input
    fasta_file = args.fasta
    output_name = args.output

    # Detect file format
    format_type = detect_file_format(input_file)
    print(f"Detected file format: {format_type}")

    if format_type == "Unknown":
        raise ValueError("Unsupported file format. Please provide GFF, GFF3 or GTF file.")

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

    print("Processing completed successfully.")

if __name__ == "__main__":
    main()

