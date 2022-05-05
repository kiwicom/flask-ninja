import pytest

from flask_ninja.security import HttpBearer


class BearerAuth(HttpBearer):
    def authenticate(self, token: str):
        return None if token != "secret" else {}


def test_bearer_missing_header(test_app):
    with test_app.test_request_context(headers={}):
        auth = BearerAuth()
        assert auth() is None


@pytest.mark.parametrize(
    ("headers", "result"),
    [
        pytest.param({}, None, id="Missing header"),
        pytest.param({"Authorization": ""}, None, id="Empty header"),
        pytest.param({"Authorization": "Foo secret"}, None, id="Wrong prefix"),
        pytest.param({"Authorization": "Bearer foo"}, None, id="Wrong token"),
        pytest.param({"Authorization": "Bearer secret"}, {}, id="OK Uppercase"),
        pytest.param({"Authorization": "bearer secret"}, {}, id="OK lowercase"),
    ],
)
def test_bearer_auth(test_app, headers, result):
    with test_app.test_request_context(headers=headers):
        auth = BearerAuth()
        assert auth() == result


def test_schema():
    assert BearerAuth().schema() == {
        "bearerTokenAuth": {"scheme": "bearer", "type": "http"}
    }
