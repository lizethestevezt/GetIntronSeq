import gzip

def detect_file_format(file_path):
    """
    Detects if a file is GFF3, GTF, or Unknown based on its content.
    Supports plain text and GZIP-compressed files.
    Returns 'GFF3', 'GTF', 'GZIP', or 'Unknown'.
    """
    # Check if the file is a GZIP file
    if file_path.endswith(".gz"):
        try:
            with gzip.open(file_path, "rt") as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue  # skip empty lines and comments
                    
                    fields = line.split("\t")
                    if len(fields) < 3:
                        return "Unknown"

                    if len(fields) >= 9:
                        attributes = fields[8]
                        if "=" in attributes:
                            return "GZIP"
                        elif '"' in attributes and ";" in attributes:
                            return "GZIP"
                        else:
                            return "Unknown"
        except Exception:
            return "Unknown"  # If the GZIP file cannot be read, return Unknown

    # Handle plain text files
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip empty lines and comments
            
            fields = line.split("\t")
            if len(fields) < 3:
                return "Unknown"

            if len(fields) >= 9:
                attributes = fields[8]
                if "=" in attributes:
                    return "GFF3"
                elif '"' in attributes and ";" in attributes:
                    return "GTF"
                else:
                    return "Unknown"

    return "Unknown"
