from unittest.mock import patch, MagicMock
from misc import check_database_members, insert_to_database

def test_fetch_compounds() -> None:
    fake_data = [
        ("Methane", -890),
        ("Ethane", -1560),
    ]
    
    with patch("misc.check_database_members.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup cursor behavior
        mock_cursor.fetchall.return_value = fake_data
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = check_database_members.fetch_compounds()
        
        expected = {
            "Methane": "-890 kJ/kmol",
            "Ethane": "-1560 kJ/kmol",
        }

        assert result == expected
        mock_cursor.execute.assert_called_once_with("SELECT Composition, Enthalpy FROM table_name;")
        mock_conn.close.assert_called_once()

def test_add_new_compound_update() -> None:
    with patch("misc.insert_to_database.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        insert_to_database.add_new_compound("Ethanol", -1366.8)

        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM table_name WHERE Composition = ?", ("Ethanol",)
        )
        mock_cursor.execute.assert_any_call(
            "UPDATE table_name SET Enthalpy = ? WHERE Composition = ?", (-1366.8, "Ethanol")
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

def test_add_new_compound_insert() -> None:
    with patch("misc.insert_to_database.sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None

        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        insert_to_database.add_new_compound("Butanol", -2671.2)

        mock_cursor.execute.assert_any_call(
            "SELECT 1 FROM table_name WHERE Composition = ?", ("Butanol",)
        )
        mock_cursor.execute.assert_any_call(
            "INSERT INTO table_name (Composition, Enthalpy) VALUES (?, ?)", ("Butanol", -2671.2)
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()