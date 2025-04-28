from input_processing import process_single_file, extract_gzip
from batch_processing import process_batch
import os
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
    parser.add_argument(
    "--batch",
    action="store_true",
    help="Enable batch processing for multiple files in a directory or GZIP archive."
    )
    args = parser.parse_args()

    # Extract arguments
    input_file = args.input
    fasta_file = args.fasta
    output_name = args.output
    batch_mode = args.batch

    # Handle GZIP files
    if input_file.endswith(".gz"):
        print(f"Extracting GZIP file: {input_file}")
        gzip_dir = os.path.splitext(input_file)[0] + "_extracted"
        extracted_file = extract_gzip(input_file, gzip_dir)
        batch_mode = True  # Set batch mode to True for GZIP extraction
        if batch_mode:
            process_batch(gzip_dir, output_name)
        else:
            process_single_file(extracted_file, fasta_file, output_name)
        return

    # Handle directories in batch mode
    if batch_mode and os.path.isdir(input_file):
        print(f"Batch processing directory: {input_file}")
        process_batch(input_file, output_name)
        return

    # Process a single file
    process_single_file(input_file, fasta_file, output_name)

if __name__ == "__main__":
    main()