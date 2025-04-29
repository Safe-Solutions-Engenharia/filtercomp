# Heat of Combustion Database

## Insert New or Update Members

This module provides functionality to connect to a local SQLite database and **insert a new record** or **update an existing one** for the enthalpy of combustion of a chemical compound.

To add or update a compound, define the following variables at the beginning of the script:

```python title="insert_to_database.py" linenums="6"
COMPOUND_NAME = 'Example compound'
HEAT_OF_COMBUSTION = -1000 # kJ/kmol
```

> This ensures the database always holds the most up-to-date information for each chemical compound.

---

## Delete a Member

This module provides functionality to connect to a local SQLite database and **delete an existing record** corresponding to the enthalpy of combustion of a chemical compound.

To delete a compound, define the following variable at the beginning of the script:

```python title="delete_from_database.py" linenums="6"
COMPOUND_NAME = 'Example compound'
```

---

## Check All Members

This module provides functionality to connect to a local SQLite database and **retrieve** the enthalpy of combustion data for all the chemical compounds inside the database.

---

## Check a Specific Member

This module provides functionality to connect to a local SQLite database and **retrieve** the enthalpy of combustion for a specific chemical compound.

To check a compound, define the following variable at the beginning of the script:

```python title="check_database_single_member.py" linenums="6"
COMPOUND_NAME = 'Example compound'
```