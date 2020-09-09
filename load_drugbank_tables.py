"""
Usage: python load_drugbank_tables.py <id> <source_dir>
<id>         - drugbank drug id (e.g. DB00007)
<source_dir> - source directory where drug json data (<id>.json) is located
"""

import psycopg2
import os
import sys
import json

from scrape_drugbank import logger, create_db_conn


def load_drug_tables(drug_id, source_file, db_conn):
    cur = db_conn.cursor()

    logger.info(f"Loading data from {source_file} to database.")

    def utf8_json(data):
        return json.dumps(data, ensure_ascii=False)

    def insert_bonds(drug_id, bond_type, bonds_array):
        for bond in bonds_array:
            cur.execute("""INSERT INTO drug_bond(drug_id, bond_type, properties) 
                           VALUES (%s, %s, %s)""", (drug_id, bond_type, utf8_json(bond)))
    with open(source_file, 'r') as json_file:
        data = json.load(json_file)

    cur.execute("""INSERT INTO drug(drug_id, drug_name, identification, pharmacology, interactions,
                                    products, categories, chemical_identifiers, "references",
                                    clinical_trials, pharmacoeconomics, properties, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (drug_id, data['Identification']['Name'], utf8_json(data['Identification']),
                 utf8_json(data['Pharmacology']), utf8_json(data['Interactions']), utf8_json(data['Products']),
                 utf8_json(data['Categories']), utf8_json(data['Chemical Identifiers']),
                 utf8_json(data['References']), utf8_json(data['Clinical Trials']),
                 utf8_json(data['Pharmacoeconomics']), utf8_json(data['Properties']), data['metadata']))

    insert_bonds(drug_id, 'target', data['Targets'])
    insert_bonds(drug_id, 'enzyme', data['Enzymes'])
    insert_bonds(drug_id, 'carrier', data['Carriers'])
    insert_bonds(drug_id, 'transporter', data['Transporters'])

    db_conn.commit()
    cur.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error(__doc__)
        sys.exit(-1)

    drug_id = sys.argv[1]
    source_dir = sys.argv[2]
    source_file = os.path.join(source_dir, f"{drug_id}.json")

    if not os.path.isfile(source_file):
        logger.error(f"Source file {source_file} doesn't exist. Exiting.")
        sys.exit(-1)

    try:
        logger.info("Initializing DB connection.")
        conn = create_db_conn()

        logger.info(f"Loading DB from {source_file}")
        load_drug_tables(drug_id, source_file, conn)
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(f"Failed to load data for {drug_id} to DB")
        logger.error(f"Error: {e}")
        sys.exit(-1)

    logger.info("Done.")
