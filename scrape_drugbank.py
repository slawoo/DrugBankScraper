"""
Usage: python scrape_drugbank.py <file>
<file> - text file containing new-line separated list of drugs ids to process (e.g. DB00007)
"""

import logging
import sys
import os
import configparser
from datetime import datetime as dt
import psycopg2


def read_config():
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    return cfg


# Initialization of global objects: config, logger and db_conn
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(filename)s - %(message)s'))
logger.addHandler(handler)
config = read_config()


def create_db_conn():
    conn = psycopg2.connect(
        host=config['db']['host'],
        database=config['db']['database'],
        user=config['db']['user'],
        password=config['db']['password']
    )
    return conn


import get_drugbank_page
import drugbank_page_to_json
import load_drugbank_tables

if __name__ == '__main__':
    # Parse command args
    if len(sys.argv) < 2:
        logger.error(__doc__)
        sys.exit(-1)

    drug_list_file = sys.argv[1]

    data_dir = config['config']['data_dir']
    target_dir = os.path.join(data_dir, dt.now().strftime('drugbank_scrub_%Y%m%d_%H%M%S'))

    if not os.path.exists(target_dir):
        logger.info(f"Creating target directory at {target_dir}")
        os.makedirs(target_dir)
    elif not os.path.isdir(target_dir):
        logger.error(f"Target path ({target_dir}) already exists and is not a directory. Exiting.")
        sys.exit(-1)

    logger.info(f"Initializing db connection.")
    conn = create_db_conn()
    if not conn:
        logger.error("Couldn't initialize db connection.")
        logger.error("Please make sure that your [db] configuration section in config.ini is correct.")
        logger.error("Additionally, please make sure that your database is up and accepting connections.")
        logger.error("Exiting.")
        sys.exit(-1)

    logger.info(f"Starting drugbank scraper (using {drug_list_file} file for a list of drug ids to process)")

    error_count = 0
    with open(drug_list_file, 'r') as f:
        for line in f.readlines():
            drug_id = line.strip()
            logger.info("Running ETL for drugbank drug id: {}".format(drug_id))
            try:
                html_file = os.path.join(target_dir, f"{drug_id}.html")
                json_file = os.path.join(target_dir, f"{drug_id}.json")
                get_drugbank_page.get_drug_page(drug_id, html_file)
                drugbank_page_to_json.drug_page_to_json(drug_id, html_file, json_file)
                load_drugbank_tables.load_drug_tables(drug_id, json_file, conn)
            except Exception as e:
                error_count += 1
                logger.error(str(e))

    logger.info("Closing DB connection.")
    conn.close()

    logger.info(
        f"Finished processing {drug_list_file} file. There were {'no' if not error_count else str(error_count)} errors.")
