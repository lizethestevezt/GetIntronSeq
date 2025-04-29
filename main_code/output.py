import sqlalchemy as sql
import zipfile
from metadata import introns, genes  # Import the table variable from metadata.py
import logging
from logger_config import setup_logger

# Setup logger
setup_logger("GetIntronSeq.log")

# Function to write FASTA files into a ZIP archive
def write_fastas_zip(engine, out_dir_name):
    """
    Writes FASTA files for each intron in the database into a ZIP archive.
    Ensures unique file names and handles duplicates gracefully.
    """
    logging.info(f"Writing FASTA files to ZIP: {out_dir_name}.zip")
    with zipfile.ZipFile(out_dir_name + ".zip", mode="w") as archive:
        with engine.connect() as conn:
            # Query the database for intron data
            result_stmt = sql.select(
                genes.c.contig,
                introns.c.intron,
                introns.c.beg,
                introns.c.end,
                introns.c.seq,
                introns.c.ori,
                introns.c.obs
            )
            result = conn.execute(result_stmt)
            rows = result.fetchall()

            # Track written file names to avoid duplicates
            written_files = set()

            # Iterate through the rows in the result
            for row in rows:
                # Create a proper FASTA file name
                name = f"{row.contig}_{row.intron}_{row.beg}-{row.end}.fasta"

                # Ensure the file name is unique
                if name in written_files:
                    logging.warning(f"Duplicate entry detected for {name}. Skipping.")
                    continue
                written_files.add(name)

                # Create the FASTA content
                fasta_content = (
                    f">{row.contig} {row.intron} {row.beg}-{row.end} {row.ori} {row.obs}\n{row.seq}\n"
                )

                # Write the content to the ZIP archive
                archive.writestr(f"{row.contig}/{name}", fasta_content)

    logging.info(f"FASTA files successfully written to {out_dir_name}.zip")
    return
