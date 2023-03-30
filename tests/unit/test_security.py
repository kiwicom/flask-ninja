from typing import Any, Optional

import pytest
from flask import Flask
from pydantic import BaseModel

from flask_ninja import NinjaAPI
from flask_ninja.models import HTTPBearer, SecuritySchemeType
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
        "bearerTokenAuth": HTTPBearer(type=SecuritySchemeType.http, scheme="bearer")
    }


@pytest.mark.parametrize(
    ("headers", "status_code"),
    [
        pytest.param({}, 401, id="Missing header"),
        pytest.param({"Authorization": "Bearer 123"}, 200, id="Correct token"),
        pytest.param({"Authorization": "123"}, 401, id="Correct token, wrong format"),
        pytest.param({"Authorization": "Bearer bla"}, 401, id="Wrong token"),
    ],
)
def test_authentication(headers, status_code):
    class MyBearer(HttpBearer):
        def authenticate(self, token: str) -> Optional[Any]:
            return token == "123" or None

    class Response(BaseModel):
        status: str

    app = Flask(__name__)
    api = NinjaAPI(app, auth=MyBearer())

    @api.get("/compute")
    def compute() -> Response:
        return Response(status="success")

    with app.test_client() as client:
        assert client.get("/compute", headers=headers).status_code == status_code
