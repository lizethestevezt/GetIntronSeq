# GetIntronSeq

This project processes genomic data to extract intron information from GFF files, updates it with sequences from FASTA files, and generates FASTA files for each intron in a structured ZIP archive. The project uses Python and SQLite for database management and sequence processing.

## Features

- Extracts intron information from GFF files.
- Creates an in-memory SQLite database to store intron data.
- Updates the database with sequences from FASTA files.
- Preprocesses multi-line FASTA files into a single-line format per contig.
- Generates FASTA files for each intron and stores them in a ZIP archive.
- Added support for handling multiple GFF and FASTA files in batch mode.
- **NEW**: Improved error handling and logging for better debugging.
- **NEW**: Dynamically handles missing introns or sequences in GFF files.
- **NEW**: Command-line arguments for flexible input/output handling.
  - Specify input files, optional FASTA files, and output names directly from the command line.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `gffutils`
  - `sqlalchemy`
  - `zipfile`
  - `logging`

Install the required libraries using pip:
```bash
pip install gffutils sqlalchemy logging
```

## File Structure

- **`main_v0.2.py`**: Main script that processes a single input file and its corresponding FASTA file (if needed).
- **`batch_processing.py`**: Handles batch processing of multiple GFF and FASTA files.
- **`metadata.py`**: Contains the database schema and metadata definitions.
- **`input_processing.py`**: Handles input file processing, including extracting intron information and checking for introns or sequences.
- **`database.py`**: Manages the SQLite database, including creating and populating tables.
- **`fasta_processing.py`**: Handles FASTA file preprocessing and updating the database with sequences.
- **`output.py`**: Generates FASTA files for each intron and stores them in a ZIP archive.
- **`logger_config.py`**: Centralized logging configuration for all scripts.
- **`file_type_validation.py`**: Detects file formats.

## Input Files

- **GFF File**: A file containing genomic annotations (e.g., `Dioscorea_dumetorum_contig1.gff`).
- **FASTA File**: A file containing genomic sequences (e.g., `Dioscorea_dumetorum_contig1.fasta`).

## Output Files

- **Extracted Introns File**: A GFF file containing intron information (e.g., `Dioscorea_dumetorum_contig1_introns.gff`).
- **Preprocessed FASTA File**: A FASTA file with single-line sequences (e.g., `Dioscorea_dumetorum_contig1_preprocessed.fasta`).
- **ZIP Archive**: A ZIP file containing FASTA files for each intron (e.g., `introns.zip`).

## Usage

### Single File Processing
1. Run the main script with the required arguments:
   ```bash
   python main_v0.2.py --input <path_to_input_file> [--fasta <path_to_fasta_file>] [--output <output_name>]
   ```
2. Arguments:
* `--input` (required): Path to the input file (GFF, GFF3, or GTF format).
* `--fasta` (optional): Path to the corresponding FASTA file (if sequences are not in the input file).
* `--output` (optional): Name of the output directory or ZIP archive (default: `introns`).
3. What the program does:
* Detects the file format of the input file.
* Checks if the input file contains introns. If not, the program exits with a message.
* Checks if the input file contains sequences:
*  * If sequences are missing, the program requires a FASTA file to be provided using the --fasta argument.
*  * If sequences are present, the program generates a FASTA file from the input file.
* Processes the input file to extract introns, create a database, and generate output files.

---

Example Commands
**Example 1: Input File with Sequences**
```bash
python main_v0.2.py --input [Dioscorea_dumetorum_contig1.gff](http://_vscodecontentref_/1) --output introns_output
````


**Example 2: Input File Without Sequences**
```bash
python main_v0.2.py --input data/no_sequences.gff --fasta [Dioscorea_dumetorum_contig1.fasta](http://_vscodecontentref_/2) --output introns_output
```


### Batch Processing
To process multiple GFF and FASTA files in batch mode, use the batch processing script:
```bash
python batch_processing.py
```

### Output
The script will generate:
- Preprocessed FASTA files (e.g., `Dioscorea_dumetorum_contig1_preprocessed.fasta`) if needed.
- A ZIP archive (`introns.zip`) containing FASTA files for each intron.

## Functions by Module

### `metadata.py`
- Defines the database schema and metadata.

### `gff_processing.py`
- **`make_introns_file(in_file, out_file)`**: Extracts intron information from a GFF file and writes it to an output file.

### `database.py`
- **`create_database(introns_file)`**: Creates an in-memory SQLite database and populates it with intron information.

### `fasta_processing.py`
- **`preprocess_fasta(fasta_file, out_file)`**: Preprocesses a FASTA file to ensure each contig's sequence is on a single line.
- **`is_fasta_preprocessed(fasta_file)`**: Checks if the FASTA file is already in the correct format (one line per sequence).
- **`add_sequences(engine, fasta_file)`**: Updates the database with sequences from the FASTA file.

### `output.py`
- **`write_fastas_zip(engine, out_dir_name)`**: Writes FASTA files for each intron in the database into a ZIP archive.

### `batch_processing.py`
- **`process_batch(input_dir, output_dir)`**: Processes multiple GFF and FASTA files in a specified directory.

## Debugging

- If the database is not updating correctly, check the `add_sequences` function for issues with `contig` matching or sequence slicing.
- Use debug prints or the logging module to verify the flow of data and the content of the database.

## Example Output

### Preprocessed FASTA File:
```
>contig1
ATCGATCGGATCGATC
>contig2
TTGGAACC
```

### Example FASTA File in ZIP Archive:
File: `contig1_intron_9878-10009.fasta`
```
>contig1 intron 9878-10009 + some_observation
ATCGATCGGATCGATC
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Created by Lizeth Estévez-Tobar.

