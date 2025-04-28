# GetIntronSeq

This project processes genomic data to extract intron information from GFF files, updates it with sequences from FASTA files, and generates FASTA files for each intron in a structured ZIP archive. The project uses Python and SQLite for database management and sequence processing.

## Features

- Extracts intron information from GFF files.
- Creates an in-memory SQLite database to store intron data.
- Updates the database with sequences from FASTA files.
- Preprocesses multi-line FASTA files into a single-line format per contig.
- Generates FASTA files for each intron and stores them in a ZIP archive.
- Added support for handling multiple GFF and FASTA files in batch mode.
- Improved error handling and logging for better debugging.
- Dynamically handles missing introns or sequences in GFF files.
- **NEW**: Command-line arguments for flexible input/output handling.
  - Specify input files, optional FASTA files, and output names directly from the command line.
- **NEW**: Automatically detects if GFF files contain sequences and prompts for a FASTA file if needed.
- **NEW**: Supports batch processing for `.gz` archives and directories containing multiple GFF and FASTA files.
- **NEW**: Handles GZIP files by extracting their contents and processing them automatically.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `gffutils`
  - `sqlalchemy`
  - `zipfile`

Install the required libraries using pip:
```bash
pip install gffutils sqlalchemy
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

- **GFF/GTF/GFF3 File**: A file containing genomic annotations (e.g., `Dioscorea_dumetorum_contig1.gff`).
- **FASTA File**: A file containing genomic sequences (e.g., `Dioscorea_dumetorum_contig1.fasta`).
- **GZIP Archive**: A `.gz` file containing multiple GFF or FASTA files.

## Output Files

- **Extracted Introns File**: A GFF file containing intron information (e.g., `Dioscorea_dumetorum_contig1_introns.gff`).
- **Preprocessed FASTA File**: A FASTA file with single-line sequences (e.g., `Dioscorea_dumetorum_contig1_preprocessed.fasta`).
- **ZIP Archive**: A ZIP file containing FASTA files for each intron (e.g., [introns.zip](http://_vscodecontentref_/0)).
- **Batch Processing Output**: For batch processing, all output files are stored in the specified output directory.

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


### Batch Processing
Batch processing allows you to process multiple GFF and FASTA files or `.gz` archives in a single run.

1. Run the main script with the `--batch` flag:
   ```bash
   python main_v0.2.py --input <path_to_directory_or_gz_file> --batch [--output <output_name>]
  ```

2. **Arguments:**

* `--input` (required): Path to the directory or .gz archive containing multiple files.
* `--batch` (required): Enables batch processing mode.
* `--output` (optional): Name of the output directory or ZIP archive (default: introns).

3. **What the program does:**
* If the input is a `.gz` archive, it extracts the archive into a temporary directory and processes all files inside.
* If the input is a directory, it processes all GFF and FASTA files in the directory.
* For each file, it checks if sequences are present in the GFF file:
  * If sequences are missing, the program prompts the user to provide the corresponding FASTA file.
* Extracts introns, creates a database, and generates output files for each file.

---

## Example Commands

**Example 1: Batch Processing for a GZIP Archive**
```bash
python main_v0.2.py --input data/multiple_files.gff.gz --batch --output introns_output
```

* **What it does:**
  * Extracts the `.gz` archive into a temporary directory.
  * Processes all GFF and FASTA files inside the archive.
  * Checks if sequences are present in each GFF file.
  * If sequences are missing, prompts the user to provide the corresponding FASTA file.
  * Generates intron files, preprocessed FASTA files, and a ZIP archive containing intron FASTA files.

**Example 2: Batch Processing for a Directory**
```bash
python main_v0.2.py --input data/input_directory --batch --output introns_output
```

* **What it does:**
  * Processes all GFF and FASTA files in the specified directory.
  * Checks if sequences are present in each GFF file.
  * If sequences are missing, prompts the user to provide the corresponding FASTA file.
  * Generates intron files, preprocessed FASTA files, and a ZIP archive containing intron FASTA files.

**Example 3: Single File with Sequences**
```bash
python main_v0.2.py --input data/Dioscorea_dumetorum_contig1.gff --output introns_output
```

* **What it does:**
  * Detects that the GFF file contains sequences.
  * Processes the file to extract introns, create a database, and generate output files.
  * Generates a ZIP archive containing intron FASTA files.

**Example 4: Single File Without Sequences**
```bash
python main_v0.2.py --input data/no_sequences.gff --fasta data/Dioscorea_dumetorum_contig1.fasta --output introns_output
```

* **What it does:**
  * Detects that the GFF file does not contain sequences.
  * Uses the provided FASTA file to add sequences to the database.
  * Processes the file to extract introns, create a database, and generate output files.
  * Generates a ZIP archive containing intron FASTA files.

---

### Output
The script will generate:
- Preprocessed FASTA files (e.g., `Dioscorea_dumetorum_contig1_preprocessed.fasta`) if needed.
- A ZIP archive (`introns.zip`) containing FASTA files for each intron.

## Debugging

- If the database is not updating correctly, check the `add_sequences` function for issues with `contig` matching or sequence slicing.
- Use debug prints or the logging module to verify the flow of data and the content of the database.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Created by Lizeth Estévez-Tobar.

