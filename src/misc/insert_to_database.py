import sqlite3

DATABASE_PATH = r'.\files\database\heat_of_combustion.db'
COMPOUND_NAME = 'Ethanol'
HEAT_OF_COMBUSTION = -1366.8 # kJ/kmol

def add_new_compound(compound_name: str, heat_of_combustion: float) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    new_row_values = (compound_name, heat_of_combustion)

    insert_query = """
        INSERT INTO table_name (Composition, Enthalpy) 
        VALUES (?, ?);
    """
    cursor.execute(insert_query, new_row_values)

    conn.commit()
    conn.close()

def main() -> None:
    add_new_compound(COMPOUND_NAME, HEAT_OF_COMBUSTION)

if __name__ == "__main__":
    main()