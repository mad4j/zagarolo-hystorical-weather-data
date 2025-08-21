import sqlite3
import json

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

def insert_metadata(conn, data):
    c = conn.cursor()
    c.execute("""
        INSERT INTO metadata (latitude, longitude, elevation, timezone, timezone_abbreviation, utc_offset_seconds, generationtime_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("latitude"),
        data.get("longitude"),
        data.get("elevation"),
        data.get("timezone"),
        data.get("timezone_abbreviation"),
        data.get("utc_offset_seconds"),
        data.get("generationtime_ms"),
    ))
    conn.commit()
    return c.lastrowid

def insert_timeseries(conn, table, metadata_id, timeseries):
    c = conn.cursor()
    if not timeseries or "time" not in timeseries:
        return
    columns = [k for k in timeseries.keys() if k != "time"]
    for i, t in enumerate(timeseries["time"]):
        values = [t]
        for col in columns:
            values.append(timeseries[col][i])
        placeholders = ", ".join(["?"] * (1 + len(columns)))
        colnames = ", ".join(["time"] + columns)
        c.execute(f"""
            INSERT INTO {table} (metadata_id, {colnames})
            VALUES (?, {placeholders})
        """, [metadata_id] + values)
    conn.commit()

def main(json_path, db_path, no_create_tables=False):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    conn = sqlite3.connect(db_path)
    metadata_id = insert_metadata(conn, data)
    if "hourly" in data:
        # Aggiungi colonne dinamiche se necessario
        cols = [k for k in data["hourly"].keys() if k != "time"]
        for col in cols:
            try:
                conn.execute(f"ALTER TABLE hourly ADD COLUMN {col} REAL")
            except sqlite3.OperationalError:
                pass
        insert_timeseries(conn, "hourly", metadata_id, data["hourly"])
    if "daily" in data:
        cols = [k for k in data["daily"].keys() if k != "time"]
        for col in cols:
            try:
                conn.execute(f"ALTER TABLE daily ADD COLUMN {col} REAL")
            except sqlite3.OperationalError:
                pass
        insert_timeseries(conn, "daily", metadata_id, data["daily"])
    conn.close()
    print(f"Importazione completata in {db_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Importa dati meteo JSON in un database SQLite.")
    parser.add_argument("json_path", help="File JSON da importare")
    parser.add_argument("db_path", help="File database SQLite")
    parser.add_argument("--no-create-tables", action="store_true", help="Non creare la struttura delle tabelle, solo append dei dati")
    args = parser.parse_args()
    main(args.json_path, args.db_path, no_create_tables=args.no_create_tables)
