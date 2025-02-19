import xml.etree.ElementTree as ET
import logging
from datetime import datetime

# Configure logging
log_file = "uniref90_parser.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def parse_uniref_xml(xml_file, output_tsv, log_interval=10000000):
    """
    Parses a large UniRef XML file and extracts UniRef90 representative entry IDs and their NCBI taxonomy IDs.
    Writes results to a TSV file and logs progress every `log_interval` entries.
    """
    start_time = datetime.now()
    logging.info(f"Starting UniRef90 XML parsing at {start_time}")

    count = 0  # Counter to track processed entries
    with open(output_tsv, "w") as out_f:
        out_f.write("uniref90_id\ttaxid\n")  # Header

        # Use iterparse to process the file efficiently
        context = ET.iterparse(xml_file, events=("end",))
        for event, elem in context:
            if elem.tag.endswith("entry"):  # Extract <entry id="...">
                uniref90_id = elem.attrib["id"]  # UniRef90 Entry ID
                taxid = None  # Placeholder for taxonomy ID

                # Locate the representative member and extract the taxonomy ID
                rep_member = elem.find(".//{http://uniprot.org/uniref}representativeMember")
                if rep_member is not None:
                    db_ref = rep_member.find("{http://uniprot.org/uniref}dbReference")
                    if db_ref is not None:
                        for prop in db_ref.findall("{http://uniprot.org/uniref}property"):
                            if prop.attrib.get("type") == "NCBI taxonomy":
                                taxid = prop.attrib["value"]
                                break  # Found taxonomy ID, stop searching

                # Write to TSV if a taxonomy ID was found
                if taxid:
                    out_f.write(f"{uniref90_id}\t{taxid}\n")
                    count += 1

                # Log progress every `log_interval` entries
                if count % log_interval == 0:
                    logging.info(f"Processed {count} entries...")

                # Free memory by clearing the processed element
                elem.clear()

    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"Parsing complete at {end_time}. Total entries processed: {count}. Time taken: {duration}")

    print(f"Parsing complete. Output saved to {output_tsv}")


# Execution
xml_file = "uniref90.xml"  # Replace with the actual path to your file
output_tsv = "uniref90_taxid_from_xml.tsv"
parse_uniref_xml(xml_file, output_tsv)
