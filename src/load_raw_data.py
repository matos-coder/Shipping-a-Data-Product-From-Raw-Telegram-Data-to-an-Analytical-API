# src/load_raw_data.py
import os
import json
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Database connection details from .env file
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = "db"  # 'localhost' Or "db"if running this script inside a Docker container
DB_PORT = "5432"

def create_raw_table(conn):
    """Creates the schema and table for raw data if they don't exist."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw_telegram;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_telegram.messages (
                raw_message_data JSONB,
                loaded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now())
            );
        """)
        print("Schema 'raw_telegram' and table 'messages' are ready.")
    conn.commit()