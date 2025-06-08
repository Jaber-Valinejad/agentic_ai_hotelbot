import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from week7_main import graph  # Or wherever the LangGraph is defined

@pytest.fixture
def mock_input_state():
    return {
        "question": "mock question",
        "generation": "",
        "intent": '',
        "sql_query": '',
        "faq_keywords": '',
        "session_id": str(datetime.now())
    }

@patch("week7_main.SupervisorAgent_")
@patch("week7_main.agent")
def test_langgraph_sql_query(mock_agent, mock_supervisor, mock_input_state):
    # Mock Supervisor response with intent "sql_query"
    fake_supervisor_instance = MagicMock()
    fake_supervisor_instance.generate_response.return_value = MagicMock(
        intent="sql_query", message="This is SQL", sql_query="SELECT * FROM users", faq_key=""
    )
    mock_supervisor.return_value = fake_supervisor_instance

    # Mock SQL agent
    mock_agent.handle_query.return_value = "Mocked SQL Result"

    result = graph.invoke(mock_input_state)
    assert result["intent"] == "sql_query"
    assert result["generation"] == "Mocked SQL Result"

@patch("week7_main.SupervisorAgent_")
@patch("week7_main.search_service1")
def test_langgraph_faq(mock_search, mock_supervisor, mock_input_state):
    # Mock Supervisor response with intent "faq"
    fake_supervisor_instance = MagicMock()
    fake_supervisor_instance.generate_response.return_value = MagicMock(
        intent="faq", message="This is FAQ", sql_query="", faq_key="refund"
    )
    mock_supervisor.return_value = fake_supervisor_instance

    # Mock FAQ agent
    mock_search.return_value = "Mocked FAQ Answer"

    result = graph.invoke(mock_input_state)
    assert result["intent"] == "faq"
    assert result["generation"] == "Mocked FAQ Answer"