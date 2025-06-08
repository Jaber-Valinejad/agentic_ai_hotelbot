import pytest
from unittest.mock import patch, MagicMock
from week7_sql import NL2SQLAgent


@patch("week7_sql.parse_to_sql")
@patch("week7_sql.engine")
def test_nl2sql_agent_handle_query(mock_engine, mock_parse_to_sql):
    # Mock the SQL generation
    mock_parse_to_sql.return_value = "SELECT * FROM rooms WHERE type ILIKE 'delux' AND base_rate < 1000"

    # Setup fake database rows
    mock_conn = MagicMock()
    mock_result = [
        ("1", "Delux", True, 300, 2),
        ("2", "Delux", True, 450, 4)
    ]
    mock_conn.execute.return_value = mock_result
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # Create agent and run test
    agent = NL2SQLAgent(db_connection=mock_engine)
    result = agent.handle_query("is there any available deluxe rooms under $1000")

    # Assertions
    assert isinstance(result, list)
    assert result[0] == ("1", "Delux", True, 300, 2)
    assert result[1][3] < 1000  # base_rate check
    mock_parse_to_sql.assert_called_once()
    mock_conn.execute.assert_called_once()


@patch("week7_sql.parse_to_sql", side_effect=Exception("OpenAI error"))
def test_nl2sql_agent_error_handling(mock_parse_to_sql):
    agent = NL2SQLAgent(db_connection=None)  # DB not needed since parse_to_sql will fail
    result = agent.handle_query("broken query")
    assert "error" in result
    assert "OpenAI error" in result["error"]