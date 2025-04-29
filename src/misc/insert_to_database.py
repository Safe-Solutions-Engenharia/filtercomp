from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / 'files' / 'database' / 'heat_of_combustion.db'
COMPOUND_NAME = 'Ethanol'
HEAT_OF_COMBUSTION = -1366.8 # kJ/kmol


def add_new_compound(compound_name: str, heat_of_combustion: float) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    check_query = "SELECT 1 FROM table_name WHERE Composition = ?"
    cursor.execute(check_query, (compound_name,))
    exists = cursor.fetchone()

    if exists:
        update_query = "UPDATE table_name SET Enthalpy = ? WHERE Composition = ?"
        cursor.execute(update_query, (heat_of_combustion, compound_name))
    else:
        insert_query = "INSERT INTO table_name (Composition, Enthalpy) VALUES (?, ?)"
        cursor.execute(insert_query, (compound_name, heat_of_combustion))

    conn.commit()
    conn.close()


def main() -> None:
    add_new_compound(COMPOUND_NAME, HEAT_OF_COMBUSTION)


if __name__ == "__main__":
    main()