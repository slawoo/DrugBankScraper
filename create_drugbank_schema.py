from scrape_drugbank import create_db_conn, logger
import psycopg2


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE drug (
                drug_id TEXT PRIMARY KEY,
                drug_name TEXT,
                identification JSON,
                pharmacology JSON,
                interactions JSON,
                products JSON,
                categories JSON,
                chemical_identifiers JSON,
                "references" JSON,
                clinical_trials JSON,
                pharmacoeconomics JSON,
                properties JSON,
                metadata TEXT
        )
        """,
        """
        CREATE OR REPLACE TABLE drug_bond (
            bond_id SERIAL PRIMARY KEY,
            drug_id TEXT NOT NULL,
            bond_type TEXT NOT NULL,
            properties JSON,
            FOREIGN KEY (drug_id)
                REFERENCES drug (drug_id)
        )
        """)

    conn = None

    try:
        logger.info("Initializing DB connection.")
        conn = create_db_conn()
        cur = conn.cursor()

        logger.info("Running CREATE TABLE commands.")
        for command in commands:
            cur.execute(command)

        cur.close()
        conn.commit()
        logger.info("Done.")
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(e)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
