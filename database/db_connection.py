import os

import psycopg2
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.

    Database credentials are loaded from environment variables
    instead of being hard-coded in the application.
    """

    host = os.getenv("DB_HOST", "localhost")
    database = os.getenv(
        "DB_NAME",
        "discussion_analysis"
    )
    user = os.getenv(
        "DB_USER",
        "myuser"
    )
    password = os.getenv(
        "DB_PASSWORD"
    )
    port = os.getenv(
        "DB_PORT",
        "5432"
    )

    if not password:
        raise RuntimeError(
            "DB_PASSWORD is not configured. "
            "Please create a .env file with your PostgreSQL credentials."
        )

    try:

        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )

        return connection

    except psycopg2.Error as e:

        raise RuntimeError(
            f"Could not connect to PostgreSQL: {e}"
        ) from e