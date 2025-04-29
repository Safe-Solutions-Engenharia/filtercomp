# Heat of Combustion Database

## Insert New or Update Members

This module provides functionality to connect to a local SQLite database and **insert a new record** or **update an existing one** for the enthalpy of combustion of a chemical compound.

To add or update a compound, define the following variables at the beginning of the script:

```python title="insert_to_database.py" linenums="5"
COMPOUND_NAME = 'Example compound'
HEAT_OF_COMBUSTION = -1000 # kJ/kmol
```

> This ensures the database always holds the most up-to-date information for each chemical compound.

---

## Delete a Member

> Not implemented yet!

---

## Check All Members

This module provides functionality to connect to a local SQLite database and **retrieve** the enthalpy of combustion data for all the chemical compounds inside the database.

---

## Check a Specific Member

> Not implemented yet!