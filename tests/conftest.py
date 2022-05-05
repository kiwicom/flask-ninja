from typing import Any, Optional

import pytest
from flask import Flask

from flask_ninja.security import HttpBearer


@pytest.fixture(scope="session")
def test_app():
    """Application instance for the tests."""
    return Flask(__name__)


@pytest.fixture(scope="session")
def test_client(test_app):
    with test_app.test_client() as client:
        yield client


class BearerAuth(HttpBearer):
    def authenticate(self, token: str) -> Optional[Any]:
        return True

    def __eq__(self, other):
        return isinstance(other, type(self))


class BearerAuthUnauthorized(HttpBearer):
    def authenticate(self, token: str) -> Optional[Any]:
        return None

    def __eq__(self, other):
        return isinstance(other, type(self))
