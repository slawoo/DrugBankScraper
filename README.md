# DrugBank Scraper

## Overview

This repo contains code for harvesting the drug related info available via drugbank.ca. It loads it into relational database (postgres) for simplified querying and research.

## Configuration

The code has been tested with Python 3.6. It requires ConfigParser, psycopg2 and BeautifulSoup4 modules to be run. You will require Postgres database to be able to load the extracted data into it.  
In order to install the dependencies please run:
```
pip install -r requirements.txt
```


#### Drugs of interest

The example 'drugs.txt' file contains a list of new-line separated DrugBank drug ids (e.g DB00007). Path (absolute or relative) to the file needs to be passed to the scraper (scrape_drugbank.py), so it knows which drug ids to process. Adjust the list to your needs. 

#### Data directory

You can specify where the scripts will store intermediate data (HTML files, JSON files). You can set this location via data_dir in [config] section of 'config.ini' file. By default, it is the current working directory.

#### DB connection/credentials

DB details (host, port, database, user, password) need to be configured in config.ini file in the [db] section.

## Running

#### Initialize db schema

If the schema is not yet present in your target database, run the following command to initialize it:
```
python create_drugbank_schema.py
```

#### Running full scraper

To run the entire process that will load the tables for all the drug ids from the input file ('drugs.txt') please execute the following command:
```
python scrape_drugbank.py drugs.txt
```

#### Step-by-step execution

In various situations (e.g. debugging code or data problem) you might want to perform the steps individually. For each drug id there are 3 steps performed:
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


#### Example queries
abc
