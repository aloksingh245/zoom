"""
Global pytest configuration.
Mocks SMTP email sending for all tests so they never hit a real mail server.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_smtp(monkeypatch):
    """
    Auto-applied to every test.
    Replaces smtplib.SMTP with a MagicMock so no real emails are sent
    and tests never fail due to SMTP credentials.
    """
    mock_server = MagicMock()
    mock_server.__enter__ = lambda s: s
    mock_server.__exit__ = MagicMock(return_value=False)

    with patch("smtplib.SMTP", return_value=mock_server):
        yield mock_server
