# DrugBank Scraper

## Overview

This repo contains code for harvesting the drug related info available via drugbank.ca. It loads it into relational database (postgres) for simplified querying and research.

## Configuration

The code has been tested with Python 3.6. It requires ConfigParser, psycopg2 and BeautifulSoup4 modules in order run. You will require Postgres database to be able to load the extracted data into it.  
In order to install the dependencies please run:
```
pip install -r requirements.txt
```


#### Drugs of interest

The example 'drugs.txt' file contains a list of new-line separated DrugBank drug ids (e.g DB00007). Path (absolute or relative) to the file needs to be passed to the scraper (scrape_drugbank.py), so it knows which drug ids to process. Adjust the list to your needs. 

#### Data directory

You can specify where the scripts will store intermediate data (HTML files, JSON files). This location needs to be set via data_dir in [config] section of 'config.ini' file. By default, it is the current working directory.

#### DB connection/credentials

DB details (host, port, database, user, password) need to be configured in config.ini file in the [db] section.

## Running

#### Initialize db schema

If the schema is not yet present in your target database, you can run the following command to initialize it.
```
python create_drugbank_schema.py
```

#### Running full scraper

Entire process, which will download the data and load the tables based on the drug ids from the input file, can be executed in one step as shown below.
```
python scrape_drugbank.py drugs.txt
```

#### Manual step-by-step execution

In various situations (e.g. debugging code or data problem) you might want to perform individual steps manually. For each drug id there are 3 steps performed:
* get drug page HTML from drugbank.ca
* convert raw HTML page to JSON data
* load target tables with the extracted drug information

Below is an example how the steps can be executed for drug id 'DB00007'.
```
$ python get_drugbank_page.py DB00007 manual
[2020-09-09 05:05:07,048] INFO - get_drugbank_page.py - Creating target directory at manual
[2020-09-09 05:05:07,049] INFO - get_drugbank_page.py - Downloading raw HTML from: https://www.drugbank.ca/drugs/DB00007
[2020-09-09 05:05:07,609] INFO - get_drugbank_page.py - Writing HTML to file: manual/DB00007.html
[2020-09-09 05:05:07,610] INFO - get_drugbank_page.py - Done.
$ python drugbank_page_to_json.py DB00007 manual manual
[2020-09-09 05:06:28,804] INFO - drugbank_page_to_json.py - Extracting data from HTML file: manual/DB00007.html
[2020-09-09 05:06:29,097] INFO - drugbank_page_to_json.py - Saving JSON data to manual/DB00007.json
[2020-09-09 05:06:29,097] INFO - drugbank_page_to_json.py - Done.
$ python load_drugbank_tables.py DB00007 manual
[2020-09-09 05:06:51,252] INFO - load_drugbank_tables.py - Initializing DB connection.
[2020-09-09 05:06:51,262] INFO - load_drugbank_tables.py - Loading DB from manual/DB00007.json
[2020-09-09 05:06:51,262] INFO - load_drugbank_tables.py - Loading data from manual/DB00007.json to database.
[2020-09-09 05:06:51,287] INFO - load_drugbank_tables.py - Done.
$
```

## Querying the data

#### Schema

Data model consists of two tables 'drug' and 'drug_bond'. These tables are in one-to-many relationship, where 'drug' is the master table for the extracted drug properties and 'drug_bonds' contains corresponding
bonds for a drug (targets, enzymes, carriers and transporters). Most of the properties for a drug, are contained in JSON fields. This is for simplicity and flexibility of the 
data model. 
```
                                  +-----------------------------+
                                  | drug                 |      |
                                  |----------------------|------|
                         +--------+ drug_id (PK)         |text  |
                         |        | drug_name            |text  |
                         |        | identification       |json  |
                         |        | pharmacology         |json  |
                         |        | interactions         |json  |
                         |        | products             |json  |
                         |        | categories           |json  |
                         |        | chemical_identifiers |json  |
                         |        | references           |json  |
                         |        | clinical_trials      |json  |
                         |        | pharmacoeconomics    |json  |
                         |        | properties           |json  |
                         |        | metadata             |text  |
                         |        +-----------------------------+
                         |
                         |        +-----------------------------+
                         |        | drug_bond            |      |
                         |        |----------------------|------|
                         |        | bond_id (PK)         |serial|
                         +------o<+ drug_id (FK)         |text  |
                                  | bond_type            |text  |
                                  | properties           |json  |
                                  +-----------------------------+
```

#### Example queries

##### Retrieve drug's DrugBank id, name, SMILES string, external ids and synonyms:
```sql
select 
  drug_id, 
  drug_name, 
  identification ->> 'External IDs' as "External IDs", 
  identification ->> 'Synonyms' as "Synonyms",
  chemical_identifiers ->> 'SMILES' as "SMILES"
from drug
where drug_id in ('DB00619', 'DB00734');
```
Result:
```
 drug_id |  drug_name  |                  External IDs                  |                                                   Synonyms                                                   |                                  SMILES                                  
---------+-------------+------------------------------------------------+--------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------
 DB00619 | Imatinib    | ["CGP-57148B"]                                 | ["Imatinib", "Imatinibum", "α-(4-methyl-1-piperazinyl)-3'-((4-(3-pyridyl)-2-pyrimidinyl)amino)-p-toluidide"] | CN1CCN(CC2=CC=C(C=C2)C(=O)NC2=CC(NC3=NC=CC(=N3)C3=CN=CC=C3)=C(C)C=C2)CC1
 DB00734 | Risperidone | ["R-64,766", "R-64766", "RCN-3028", "RCN3028"] | ["Risperidona", "Rispéridone", "Risperidone", "Risperidonum"]                                                | CC1=C(CCN2CCC(CC2)C2=NOC3=C2C=CC(F)=C3)C(=O)N2CCCCC2=N1
(2 rows)

```

##### Retrieve Gene Name and Actions for every Target of a drug:
```sql
select 
  d.drug_id, 
  d.drug_name, 
  db.properties ->> 'Gene Name' as "Gene Name", 
  db.properties ->> 'Actions' as "Actions" 
from drug d 
join drug_bond db on db.drug_id=d.drug_id 
where 
  db.bond_type='target'
  and d.drug_id = 'DB00619';
```

Result:
```
 drug_id | drug_name | Gene Name |            Actions            
---------+-----------+-----------+-------------------------------
 DB00619 | Imatinib  | BCR       | ["Inhibitor"]
 DB00619 | Imatinib  | KIT       | ["Antagonist", "Multitarget"]
 DB00619 | Imatinib  | RET       | ["Inhibitor"]
 DB00619 | Imatinib  | NTRK1     | ["Antagonist"]
 DB00619 | Imatinib  | CSF1R     | ["Antagonist"]
 DB00619 | Imatinib  | PDGFRA    | ["Antagonist"]
 DB00619 | Imatinib  | DDR1      | ["Antagonist"]
 DB00619 | Imatinib  | ABL1      | ["Inhibitor"]
 DB00619 | Imatinib  | PDGFRB    | ["Antagonist"]
(9 rows)
```