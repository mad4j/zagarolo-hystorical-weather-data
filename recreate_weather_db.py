#!/usr/bin/env python3
"""
Script per ricreare un database SQLite meteorologico da zero e importare tutti i file JSON presenti in una cartella.

- Cancella il database esistente (se presente)
- Crea la struttura con create_weather_db.py
- Importa tutti i file JSON da una cartella con import_weather_json_to_sqlite.py

Uso:
  python recreate_weather_db.py [--db weather.db] [--data-dir weather_data/]
"""

import os
import sys
import argparse
import subprocess

DEFAULT_DB = "weather.db"
DEFAULT_DATA_DIR = "weather_data"


def main():
    parser = argparse.ArgumentParser(description="Ricrea il database meteo e importa tutti i file JSON disponibili.")
    parser.add_argument('--db', type=str, default=DEFAULT_DB, help=f"Nome database SQLite (default: {DEFAULT_DB})")
    parser.add_argument('--data-dir', type=str, default=DEFAULT_DATA_DIR, help=f"Cartella con file JSON (default: {DEFAULT_DATA_DIR})")
    args = parser.parse_args()

    db_path = args.db
    data_dir = args.data_dir

    # 1. Cancella il database esistente
    if os.path.exists(db_path):
        print(f"Rimuovo database esistente: {db_path}")
        os.remove(db_path)
    else:
        print(f"Database {db_path} non esistente, nessuna rimozione necessaria.")

    # 2. Crea la struttura del database
    print(f"Creo la struttura del database in {db_path}...")
    result = subprocess.run([sys.executable, "create_weather_db.py", db_path])
    if result.returncode != 0:
        print("Errore nella creazione della struttura del database.")
        sys.exit(1)

    # 3. Importa tutti i file JSON
    if not os.path.isdir(data_dir):
        print(f"Cartella dati non trovata: {data_dir}")
        sys.exit(1)

    json_files = [f for f in os.listdir(data_dir) if f.endswith(".json") and f.startswith("weather_")]
    if not json_files:
        print(f"Nessun file JSON trovato in {data_dir}")
        sys.exit(1)

    print(f"Importo {len(json_files)} file JSON in {db_path}...")
    for i, filename in enumerate(sorted(json_files)):
        json_path = os.path.join(data_dir, filename)
        print(f"[{i+1}/{len(json_files)}] Importo {filename}...")
        result = subprocess.run([sys.executable, "import_weather_json_to_sqlite.py", json_path, db_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Errore nell'importazione di {filename}: {result.stderr}")
        else:
            print(f"Importazione di {filename} completata.")

    print("Operazione completata.")

if __name__ == "__main__":
    main()
