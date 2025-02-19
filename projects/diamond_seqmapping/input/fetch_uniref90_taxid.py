import requests
from requests.adapters import HTTPAdapter, Retry
import re
import urllib.parse
import logging
from datetime import datetime

# Configure logging to write progress to a file
logging.basicConfig(
    filename="uniref90_fetch.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Regex for extracting the "next" page link
re_next_link = re.compile(r'<(.+)>; rel="next"')

# Configure retries for handling API failures
retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))


def get_next_link(headers):
    """Extracts the next page link from response headers if available."""
    if "Link" in headers:
        match = re_next_link.search(headers["Link"])
        if match:
            return match.group(1)  # Extract next page URL
    return None


def get_batch(batch_url):
    """Fetch data in batches from the UniProt API."""
    while batch_url:
        response = session.get(batch_url)
        response.raise_for_status()  # Stop if a request fails

        total = response.headers.get("x-total-results", "Unknown")  # Total entries
        yield response, total

        batch_url = get_next_link(response.headers)  # Get next cursor URL


# --- UniRef90 API Configuration ---
base_url = "https://rest.uniprot.org/uniref/search"
query_params = {
    "query": "identity:0.9",  # UniRef90 clusters
    "fields": "id,organism_id",  # ✅ Correct field for the representative taxonomy ID
    "format": "tsv",  # Get results as TSV
    "size": 500,  # Entries per batch
}
encoded_params = urllib.parse.urlencode(query_params)  # Encode query parameters
url = f"{base_url}?{encoded_params}"  # Construct full URL

# --- Output file ---
output_file = "uniref90_taxid.tsv"

# Open file and write headers
with open(output_file, "w", encoding="utf-8") as f:
    f.write("id\torganism_id\n")  # Column headers

    total_entries = 0  # Track total entries processed

    # Fetch data in batches
    for batch, total in get_batch(url):
        for line in batch.text.splitlines()[1:]:  # Skip header row
            try:
                uniref_id, organism_id = line.split("\t")

                # Keep only the representative taxonomy ID
                organism_id = organism_id.split(";")[0].strip()  # ✅ Only the first tax ID

                # Write to file immediately
                f.write(f"{uniref_id}\t{organism_id}\n")

                total_entries += 1

                # Log progress every 1,000,000 entries
                if total_entries % 1000000 == 0:
                    logging.info(f"Processed {total_entries} entries at {datetime.now()}")

            except ValueError as e:
                logging.exception(f"Skipping malformed line: {line} - Error: {e}")

    logging.info(f"Completed fetching UniRef90 data. Total entries: {total_entries}")
    print(f"Results saved to {output_file}")
