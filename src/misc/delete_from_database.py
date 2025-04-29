from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / 'files' / 'database' / 'heat_of_combustion.db'
COMPOUND_NAME = 'Ethanol'

def delete_compound(compound_name: str) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    delete_query = "DELETE FROM table_name WHERE Composition = ?"
    cursor.execute(delete_query, (compound_name,))

    conn.commit()
    conn.close()

def main() -> None:
    delete_compound(COMPOUND_NAME)

if __name__ == "__main__":
    main()
