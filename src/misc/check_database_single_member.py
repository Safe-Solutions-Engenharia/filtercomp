from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / 'files' / 'database' / 'heat_of_combustion.db'
COMPOUND_NAME = 'Ethanol'

def fetch_compound(composition: str) -> str | None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    select_query = "SELECT Enthalpy FROM table_name WHERE Composition = ?;"
    cursor.execute(select_query, (composition,))

    row = cursor.fetchone()

    conn.close()

    if row:
        return f'{row[0]} kJ/kmol'
    else:
        return None

def main() -> None:
    enthalpy = fetch_compound(COMPOUND_NAME)

    if enthalpy:
        print(f'{COMPOUND_NAME}: {enthalpy}')
    else:
        print(f'{COMPOUND_NAME} not found in database.')

if __name__ == "__main__":
    main()
