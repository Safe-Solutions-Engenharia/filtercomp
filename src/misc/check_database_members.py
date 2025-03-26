import sqlite3

DATABASE_PATH = r'.\files\database\heat_of_combustion.db'

def fetch_compounds() -> dict:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    select_query = "SELECT Composition, Enthalpy FROM table_name;"
    cursor.execute(select_query)

    rows = cursor.fetchall()
    compounds_dict = {row[0]: f'{row[1]} kJ/kmol' for row in rows}

    conn.close()

    return compounds_dict

def main() -> None:
    compounds = fetch_compounds()
    print(compounds)

if __name__ == "__main__":
    main()
