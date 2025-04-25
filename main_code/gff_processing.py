import gffutils
import logging
from logger_config import setup_logger
# Setup logger
setup_logger("GetIntronSeq.log")
# Function to create an introns file from a GFF file
def make_introns_file(in_file):
    """
    Creates an output file containing intron information extracted from a GFF file.
    """
    out_file = "data/" + in_file.replace(".gff", "_introns.gff")
    logging.info(f"Creating introns file from GFF: {in_file}")
    db = gffutils.create_db(in_file, dbfn=":memory:", id_spec=None, verbose=True, merge_strategy="create_unique", force=True)
    with open(out_file, 'w') as fout:
        for intron in db.create_introns("exon"):
            fout.write(str(intron) + "\n")
    return out_file
