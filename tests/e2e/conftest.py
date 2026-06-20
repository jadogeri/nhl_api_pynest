"""
E2E test setup.

Imports the real FastAPI app and resets the database state before every
test by calling POST /teams/truncate through the TestClient. This works
regardless of which database file the app is using, and avoids the
module-reload/patch conflict that caused the in-memory approach to fail.

The DATABASE_URL is set to sqlite:///./test_nhl.db by tests/conftest.py
(via os.environ.setdefault) before any module imports, so the app writes
to a dedicated test file and never touches national_hockey_league.db.
"""
import pytest
from starlette.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.app_module import http_server
    return TestClient(http_server, raise_server_exceptions=True)


@pytest.fixture(autouse=True)
def clear_teams_between_tests(client):
    """Truncate teams before every e2e test for a clean slate."""
    client.post("/teams/truncate")
    yield
