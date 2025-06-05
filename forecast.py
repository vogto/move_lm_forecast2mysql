import os
import csv
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import mysql.connector

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starte Script ...")

load_dotenv()

LOCAL_PATH = os.getenv("LOCAL_PATH")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

def get_latest_file():
    files = [f for f in os.listdir(LOCAL_PATH) if f.lower().endswith('.csv')]
    if not files:
        raise FileNotFoundError("Keine CSV-Dateien im Verzeichnis gefunden.")

    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(LOCAL_PATH, f)))
    latest_file_path = os.path.join(LOCAL_PATH, latest_file)
    print(f"Verwende neueste Datei: {latest_file} (geändert am {datetime.fromtimestamp(os.path.getmtime(latest_file_path))})")
    return latest_file_path

def import_csv_to_mysql(filepath):
    filename_only = os.path.basename(filepath)
    print(f"Lese Datei: {filepath}")

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    cursor = connection.cursor()

    print("Leere Tabelle forecast_to_home24 ...")
    cursor.execute("TRUNCATE TABLE forecast_to_home24")

    with open(filepath, mode='r', encoding='cp1252', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        header = next(reader)
        print(f"Header: {header}")

        for row in reader:
            if row and row[-1] == '':
                row = row[:-1]

            if len(row) != 11:
                print(f"Überspringe Zeile mit {len(row)} Spalten: {row}")
                continue

            if row[8]:
                row[8] = row[8].replace(',', '.')

            aktuelles_datum = datetime.now(ZoneInfo("Europe/Berlin")).strftime('%Y-%m-%d %H:%M:%S')
            row.append(aktuelles_datum)
            row.append(filename_only)  # Dateiname hinzufügen

            sql = """
                INSERT INTO forecast_to_home24 (
                    ArtikelId, StandortId, LieferantenId, Übertragungsdatum, Bestelldatum,
                    Lieferdatum, Filialdatum, Verfügbarkeitsdatum, Bestellmenge, Kundenauftrag,
                    Username, Datum, FileName
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, row)

    connection.commit()
    cursor.close()
    connection.close()
    print("Import abgeschlossen.")

def main():
    try:
        filepath = get_latest_file()
        import_csv_to_mysql(filepath)
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()