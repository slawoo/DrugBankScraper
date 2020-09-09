"""
Usage: python get_drugbank_page.py <id> <target_dir>
<id>         - drugbank drug id (e.g. DB00007)
<target_dir> - target directory where the retrieved drug page html will be saved
"""
import requests
import sys
import os

from scrape_drugbank import logger


def get_drug_page(drug_id, target_file):
    url_base = "https://www.drugbank.ca/drugs/"
    drug_url = url_base + drug_id

    logger.info(f"Downloading raw HTML from: {drug_url}")
    try:
        page = requests.get(drug_url)
    except Exception as e:
        logger.error(f"Couldn't successfully complete GET request to {drug_url}")
        raise e

    logger.info(f"Writing HTML to file: {target_file}")
    with open(target_file, 'w') as f:
        f.write(page.text)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error(__doc__)
        sys.exit(-1)

    drug_id = sys.argv[1]
    target_dir = sys.argv[2]

    if not os.path.exists(target_dir):
        logger.info(f"Creating target directory at {target_dir}")
        os.makedirs(target_dir)
    elif not os.path.isdir(target_dir):
        logger.error(f"Target path ({target_dir}) already exists and is not a directory. Exiting.")
        sys.exit(-1)

    target_html_file = os.path.join(target_dir, f"{drug_id}.html")

    try:
        get_drug_page(drug_id, target_html_file)
    except Exception as e:
        logger.error(f"Couldn't successfully retrieve HTML for drug id {drug_id}")
        sys.exit(-1)

    logger.info("Done.")
