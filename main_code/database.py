import sqlalchemy as sql
from metadata import metadata, genes, introns  # Importing table definitions from metadata.py
from logger_config import setup_logger
# Setup logger
setup_logger("GetIntronSeq.log")
# This script creates an SQLite database in memory and populates it with intron information from a GFF file.

def create_database(introns_file):
    """
    Creates an in-memory SQLite database and populates it with:
    1. A table for genes per contig.
    2. A table for introns per gene.
    """
    engine = sql.create_engine("sqlite+pysqlite:///:memory:", echo=True)
    metadata.create_all(engine)  # Create the table structure in the database using the defined schema

    with open(introns_file, "r") as file:
        with engine.begin() as conn:
            seen_genes = set()  # A set for temporary storage of genes to avoid duplicates
            gene_intron_counter = {}  # rack number of introns per gene

            for line in file:
                # Parse the intron information and insert it into the database
                fields = line.strip().split("\t")
                contig = fields[0]
                gene = fields[8].split(";")[0].split("=")[-1].strip(".t1")  # Extract gene name from attributes
                beg = int(fields[3])
                end = int(fields[4])
                ori = fields[6]
                obs = fields[8]

                # Insert into the genes table if the gene is not already added
                if (contig, gene) not in seen_genes:
                    conn.execute(genes.insert().values(
                        contig=contig,
                        gene=gene
                    ))
                    seen_genes.add((contig, gene))
                    gene_intron_counter[gene] = 1  # Start counting introns from 1
                else:
                    gene_intron_counter[gene] += 1

                intron_name = f"intron{gene_intron_counter[gene]}"

                # Insert into the introns table
                conn.execute(introns.insert().values(
                    gene=gene,
                    intron=intron_name,
                    beg=beg,
                    end=end,
                    seq="",  # Leave empty since it will be updated later
                    ori=ori,
                    obs=obs
                ))

    return engine
