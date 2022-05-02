import pytest
from flask import Flask


@pytest.fixture(scope="session")
def test_app():
    """Application instance for the tests."""
    return Flask(__name__)


@pytest.fixture(scope="session")
def test_client(test_app):
    with test_app.test_client() as client:
        yield client
