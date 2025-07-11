# src/load_raw_data.py
import os
import json
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

load_dotenv()
# Database connection details from .env file
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = "localhost"  # 'localhost' Or "db"if running this script inside a Docker container
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

def load_jsonl_to_db(conn, file_path: Path):
    """Loads a single JSONL file into the raw_telegram.messages table."""
    print(f"Processing file: {file_path.name}")
    with file_path.open('r', encoding='utf-8') as f:
        with conn.cursor() as cur:
            for line in f:
                try:
                    data = json.loads(line)
                    cur.execute(
                        "INSERT INTO raw_telegram.messages (raw_message_data) VALUES (%s);",
                        (json.dumps(data),)
                    )
                except json.JSONDecodeError:
                    print(f"Skipping malformed line in {file_path.name}: {line}")
    conn.commit()

def main():
    """Main function to orchestrate the loading process."""
    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        ) as conn:
            print("Successfully connected to PostgreSQL.")
            create_raw_table(conn)

            # Define the path to your data lake
            project_root = Path(__file__).resolve().parent.parent
            data_lake_path = project_root / "data" / "raw" / "telegram_messages"

            # Iterate through all date folders and jsonl files
            for date_folder in data_lake_path.iterdir():
                if date_folder.is_dir():
                    for json_file in date_folder.glob("*.jsonl"):
                        load_jsonl_to_db(conn, json_file)

            print("All files processed successfully.")

    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database. Is it running? Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()