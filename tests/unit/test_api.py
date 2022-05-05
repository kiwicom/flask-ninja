# pylint: disable=unused-argument
import json

import pytest
from flask import Flask

from flask_ninja.api import NinjaAPI, Server
from flask_ninja.router import Router
from tests.conftest import BearerAuth


@pytest.fixture
def api():
    app = Flask(__name__)
    return NinjaAPI(app)


def test_api_add_router_without_prefix(api):
    api_router = Router()

    @api_router.get("/endpoint_api")
    def endpoint_router() -> int:
        return 1

    api.add_router(api_router)

    client = api.router.app.test_client()
    resp = client.get("/endpoint_api")
    assert resp.status_code == 200
    assert resp.json == 1


def test_api_add_router_with_prefix(api):
    api_router = Router()

    @api_router.get("/endpoint_api")
    def endpoint_router() -> int:
        return 1

    api.add_router(api_router, prefix="/prefix")

    client = api.router.app.test_client()
    resp = client.get("/prefix/endpoint_api")
    assert resp.status_code == 200
    assert resp.json == 1


def test_api_get(api):
    @api.get("/endpoint_api_get")
    def endpoint_api_get() -> int:
        return 2

    resp = api.router.app.test_client().get("/endpoint_api_get")
    assert resp.json == 2


def test_api_post(api):
    @api.post("/endpoint_api_post")
    def endpoint_api_post() -> int:
        return 2

    resp = api.router.app.test_client().post("/endpoint_api_post")
    assert resp.json == 2


def test_api_put(api):
    @api.put("/endpoint_api_put")
    def endpoint_api_put() -> int:
        return 2

    resp = api.router.app.test_client().put("/endpoint_api_put")
    assert resp.json == 2


def test_api_patch(api):
    @api.patch("/endpoint_api_patch")
    def endpoint_api_patch() -> int:
        return 2

    resp = api.router.app.test_client().patch("/endpoint_api_patch")
    assert resp.json == 2


def test_api_delete(api):
    @api.delete("/endpoint_api_delete")
    def endpoint_api_delete() -> int:
        return 2

    resp = api.router.app.test_client().delete("/endpoint_api_delete")
    assert resp.json == 2


def test_get_schema(api, snapshot):
    @api.get("/some_endpoint/<int:param>", auth=BearerAuth())
    def endpoint_api_get(param: int, server: Server) -> int:
        return 2

    snapshot.assert_match(json.dumps(api.get_schema()), "api_schema")
