import pytest
from unittest.mock import patch, MagicMock
import helpers

def test_timestamp_now():
    """
    Test the timestamp_now function.

    This function checks if the timestamp_now function returns an integer.
    """
    assert isinstance(helpers.timestamp_now(), int)

def test_format_user():
    """
    Test the format_user function.

    This function checks if the format_user function correctly formats the user data.
    """
    name = "test_user"
    time = helpers.timestamp_now()
    ip = "192.168.1.1"
    upload = 5 
    download = 10 
    upload_total = 50 * 10**6
    download_total = 100 * 10**6
    
    result = helpers.format_user(name, time, ip, upload, download, upload_total, download_total)
    
    assert result["name"] == "test_user"
    assert result["ip"] == "192.168.1.1"
    assert result["upload"] == "5 M/s"
    assert result["download"] == "10 M/s"
    assert result["upload_total"] == "50 M"
    assert result["download_total"] == "100 M"

@patch('helpers.get_db')
def test_add_alert(mock_get_db):
    """
    Test the add_alert function.

    This function checks if the add_alert function correctly adds an alert to the database.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    helpers.add_alert("Test Alert", "This is a test alert", True)
    
    mock_cursor.execute.assert_called_with(
        "INSERT INTO alerts (Title, Body, Timestamp, Severe) VALUES (%s, %s, %s, %s);",
        ("Test Alert", "This is a test alert", helpers.timestamp_now(), True)
    )
