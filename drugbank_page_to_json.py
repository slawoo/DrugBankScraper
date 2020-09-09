"""
Usage: python drugbank_page_to_json.py <id> <source_dir> <target_dir>
<id>         - drugbank drug id (e.g. DB00007)
<source_dir> - source directory where the raw html of a drug page (<id>.html) is located
<target_dir> - target directory where the data in json format (<id>.json) will be saved
"""

from bs4 import BeautifulSoup
import os
import sys
import json

from scrape_drugbank import logger

def drug_page_to_json(drug_id, source_file, target_file):
    section_to_id = {
        'Identification': 'identification-header',
        'Pharmacology': 'pharmacology-header',
        'Interactions': 'interactions-header',
        'Products': 'products-header',
        'Categories': 'categories-header',
        'Chemical Identifiers': 'chemical-identifiers-header',
        'References': 'references-header',
        'Clinical Trials': 'clinical-trials-header',
        'Pharmacoeconomics': 'pharmacoeconomics-header',
        'Properties': 'properties-header'
    }
    targets_id = 'targets'
    enzymes_id = 'enzymes'
    carriers_id = 'carriers'
    transporters_id = 'transporters'
    metadata_id = 'drug-meta'

    def extract_bonds(bond_name, bond_id, data):
        extracted_data[bond_name] = []
        bonds_div = soup.find(id=bond_id)

        if bonds_div:
            for bond_div in bonds_div.find_all('div', {'class': 'bond card'}):
                bond = {}
                bond['Molecule name'] = bond_div.find('div', {'class': 'card-header'}).find('strong').text.split(' ', 1)[1]
                keys = bond_div.find_all('dt')
                vals = bond_div.find_all('dd')
                for k, v in zip(keys, vals):
                    list_vals = v.find_all('div')
                    if list_vals:
                        list_vals = [lv.text.strip() for lv in list_vals]
                    bond[k.text] = v.text.strip() if not list_vals else list_vals
                extracted_data[bond_name].append(bond)

    logger.info(f"Extracting data from HTML file: {source_file}")
    with open(source_file, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    extracted_data = {}

    for section in section_to_id:
        section_header = soup.find(id=section_to_id[section])
        dl = section_header.find_next()
        keys = [tag.text.strip() for tag in dl.find_all('dt')]
        vals = [tag.text.strip() for tag in dl.find_all('dd')]
        extracted_data[section] = {}
        for k, v in zip(keys, vals):
            extracted_data[section][k] = v

    extract_bonds('Targets', targets_id, extracted_data)
    extract_bonds('Enzymes', enzymes_id, extracted_data)
    extract_bonds('Carriers', carriers_id, extracted_data)
    extract_bonds('Transporters', transporters_id, extracted_data)

    extracted_data['metadata'] = soup.find(id=metadata_id).text

    logger.info(f"Saving JSON data to {target_file}")
    with open(target_file, 'w') as f:
        f.write(json.dumps(extracted_data, indent=4))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        logger.error(__doc__)
        sys.exit(-1)

    drug_id = sys.argv[1]
    source_dir = sys.argv[2]
    target_dir = sys.argv[3]
    source_file = os.path.join(source_dir, f"{drug_id}.html")
    target_file = os.path.join(target_dir, f"{drug_id}.json")

    if not os.path.isfile(source_file):
        logger.error(f"Source file {source_file} doesn't exist. Exiting.")
        sys.exit(-1)

    if not os.path.exists(target_dir):
        logger.info(f"Creating target directory at {target_dir}")
        os.makedirs(target_dir)
    elif not os.path.isdir(target_dir):
        logger.error(f"Target path ({target_dir}) already exists and is not a directory. Exiting.")
        sys.exit(-1)

    try:
        drug_page_to_json(drug_id, source_file, target_file)
    except Exception as e:
        logger.error(f"Couldn't successfuly convert {source_file} to JSON")
        logger.error(f"Error message: {e}")
        sys.exit(-1)

    logger.info("Done.")