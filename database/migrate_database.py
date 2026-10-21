# database/migrate_database.py
import psycopg2
import os
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Executes the schema.sql file to initialize or update the database."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable is missing.")
        return False

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    try:
        with open(schema_path, 'r') as file:
            sql_script = file.read()

        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_script)
            conn.commit()
        logger.info("Database migration completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to migrate database: {e}")
        return False

if __name__ == "__main__":
    run_migrations()
