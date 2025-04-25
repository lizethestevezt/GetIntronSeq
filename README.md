# GetIntronSeq

This project processes genomic data to extract intron information from GFF files, updates it with sequences from FASTA files, and generates FASTA files for each intron in a structured ZIP archive. The project uses Python and SQLite for database management and sequence processing.

## Features

- Extracts intron information from GFF files.
- Creates an in-memory SQLite database to store intron data.
- Updates the database with sequences from FASTA files.
- Preprocesses multi-line FASTA files into a single-line format per contig.
- Generates FASTA files for each intron and stores them in a ZIP archive.
- **NEW**: Added support for handling multiple GFF and FASTA files in batch mode.
- **NEW**: Improved error handling and logging for better debugging.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `gffutils`
  - `sqlalchemy`
  - `zipfile`
  - **NEW**: `logging`

Install the required libraries using pip:
```bash
pip install gffutils pandas sqlalchemy logging
```

## File Structure

- **`main.py`**: Main script that orchestrates the workflow by calling functions from other modules.
- **`metadata.py`**: Contains the database schema and metadata definitions.
- **`gff_processing.py`**: Handles GFF file processing, including extracting intron information.
- **`database.py`**: Manages the SQLite database, including creating and populating tables.
- **`fasta_processing.py`**: Handles FASTA file preprocessing and updating the database with sequences.
- **`output.py`**: Generates FASTA files for each intron and stores them in a ZIP archive.
- **`batch_processing.py`**: **NEW**: Handles batch processing of multiple GFF and FASTA files.
- **Input Files**:
  - `Dioscorea_dumetorum_contig1.gff`: Example GFF file containing genomic annotations.
  - `Dioscorea_dumetorum_contig1.fasta`: Example FASTA file containing genomic sequences.
- **Output Files**:
  - `Dioscorea_dumetorum_contig1_introns.gff`: Extracted intron information from the GFF file.
  - `Dioscorea_dumetorum_contig1_preprocessed.fasta`: Preprocessed FASTA file with single-line sequences.
  - `introns.zip`: ZIP archive containing FASTA files for each intron.

## Usage

### Prepare Input Files
Place your GFF files (e.g., `Dioscorea_dumetorum_contig1.gff`) and FASTA files (e.g., `Dioscorea_dumetorum_contig1.fasta`) in the same directory as the script.

### Run the Script
Execute the script using Python:
```bash
python main_v0.2.py
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

