import unittest
from unittest.mock import patch, MagicMock
import sql

class TestSql(unittest.TestCase):
    """
    A test case for the sql module.
    """

    @patch('sql.mysql.connector.connect')
    def test_get_db(self, mock_connect):
        """
        Test the get_db function by mocking mysql.connector.connect.
        """
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        db = sql.get_db()
        
        # Ensure the connection function was called
        mock_connect.assert_called_once()
        
        # Check that the return value is the mock_db object
        self.assertEqual(db, mock_db)

    @patch('sql.get_db')
    def test_setup_db(self, mock_get_db):
        """
        Test the setup_db function by mocking the database and cursor.
        """
        mock_conn = MagicMock()  # Mock the database connection
        mock_cursor = MagicMock()  # Mock the cursor object
        mock_get_db.return_value = mock_conn  # Mock get_db() to return the mock connection
        mock_conn.cursor.return_value = mock_cursor  # Mock cursor() to return the mock cursor
        
        # Call the setup_db function
        sql.setup_db()
        
        # Ensure the cursor execute method was called with SQL commands
        mock_cursor.execute.assert_called()
        
        # Ensure commit was called to save changes
        mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
