def detect_file_format(file_path):
    """
    Detects if a file is GFF3, GTF, BED, or Unknown based on its content.
    Returns 'GFF3', 'GTF', 'BED', or 'Unknown'.
    """
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip empty lines and comments
            
            fields = line.split("\t")
            if len(fields) < 3:
                return "Unknown"

            if len(fields) == 3 or len(fields) == 6 or len(fields) >= 12:
                # BED files usually have 3-12 fields, but NO attributes section like GFF
                if all(field.replace(".", "").replace("-", "").isalnum() for field in fields[:3]):
                    return "Unknown"  # BED format is not supported in this context

            if len(fields) >= 9:
                attributes = fields[8]
                if "=" in attributes:
                    return "GFF3"
                elif '"' in attributes and ";" in attributes:
                    return "GTF"
                else:
                    return "Unknown"

    return "Unknown"
