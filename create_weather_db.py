import sqlite3
import argparse

def create_tables(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY,
            latitude REAL,
            longitude REAL,
            elevation REAL,
            timezone TEXT,
            timezone_abbreviation TEXT,
            utc_offset_seconds INTEGER,
            generationtime_ms REAL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS hourly (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metadata_id INTEGER,
            time TEXT,
            FOREIGN KEY(metadata_id) REFERENCES metadata(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metadata_id INTEGER,
            time TEXT,
            FOREIGN KEY(metadata_id) REFERENCES metadata(id)
        )
    """)
    conn.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea un database SQLite con la struttura per i dati meteo.")
    parser.add_argument("db_path", help="File database SQLite da creare")
    args = parser.parse_args()
    conn = sqlite3.connect(args.db_path)
    create_tables(conn)
    conn.close()
    print(f"Database creato con struttura in {args.db_path}")
