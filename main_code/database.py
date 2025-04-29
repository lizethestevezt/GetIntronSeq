import sqlalchemy as sql
from metadata import metadata, genes, introns  # Importing table definitions from metadata.py
from logger_config import setup_logger
import logging
# Setup logger
setup_logger("GetIntronSeq.log")
# This script creates an SQLite database in memory and populates it with intron information from a GFF file.

def create_database(introns_file):
    """
    Creates an in-memory SQLite database and populates it with:
    1. A table for genes per contig.
    2. A table for introns per gene, enumerating introns as "intron1", "intron2", etc.
    Ensures no duplicate entries are added efficiently.
    """
    engine = sql.create_engine("sqlite+pysqlite:///:memory:", echo=False)
    metadata.create_all(engine)  # Create the table structure in the database using the defined schema

    with open(introns_file, "r") as file:
        with engine.begin() as conn:
            # Fetch all existing genes and introns into memory
            existing_genes = {
                row.gene: row.contig for row in conn.execute(sql.select(genes.c.gene, genes.c.contig)).fetchall()
            }
            existing_introns = {
                gene: set(
                    (row.beg, row.end, row.ori)
                    for row in conn.execute(
                        sql.select(introns.c.beg, introns.c.end, introns.c.ori).where(introns.c.gene == gene)
                    )
                )
                for gene in existing_genes
            }

            # Initialize intron counts for each gene
            intron_counts = {gene: len(existing_introns[gene]) for gene in existing_genes}

            for line in file:
                # Parse the intron information
                fields = line.strip().split("\t")
                contig = fields[0]
                gene = fields[8].split(";")[0].split("=")[-1].strip(".t1")  # Extract gene name
                beg = int(fields[3])
                end = int(fields[4])
                ori = fields[6]
                obs = fields[8]

                # Add the gene to the genes table if not already added
                if gene not in existing_genes:
                    conn.execute(
                        genes.insert().values(
                            contig=contig,
                            gene=gene
                        )
                    )
                    existing_genes[gene] = contig
                    existing_introns[gene] = set()
                    intron_counts[gene] = 0

                # Check if the intron already exists
                if (beg, end, ori) in existing_introns[gene]:
                    continue  # Skip duplicate intron

                # Increment the intron count for the gene
                intron_counts[gene] += 1
                intron_number = f"intron{intron_counts[gene]}"

                # Add the intron to the introns table
                conn.execute(
                    introns.insert().values(
                        gene=gene,
                        intron=intron_number,
                        beg=beg,
                        end=end,
                        ori=ori,
                        obs=obs
                    )
                )
                existing_introns[gene].add((beg, end, ori))

    logging.info("Database created successfully.")
    return engine