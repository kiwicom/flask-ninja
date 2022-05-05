# pylint: disable=protected-access, unused-argument,disallowed-name
from datetime import datetime
from typing import Union
from unittest.mock import MagicMock

import pytest

from flask_ninja.api import Server
from flask_ninja.operation import (
    ApiConfigError,
    Callback,
    Operation,
    SerializationModel,
)
from flask_ninja.param import Param, ParamType
from tests.conftest import BearerAuth, BearerAuthUnauthorized


def view_func_str() -> str:
    pass


def view_func_pydantic_object(bid: int, server: Server) -> Server:
    """Some title.

    Some long description

    :param int bid: Some int
    :param Server server: Some server
    """
    return Server(url=str(bid), description=server.description)  # some return value


def view_func_list() -> list[Server]:
    pass


def view_func_list_dict() -> list[dict[str, Server]]:
    pass


def view_func_union() -> Union[list[Server], dict[str, Server]]:
    pass


def view_func_none_return() -> None:
    pass


@pytest.mark.parametrize(
    ("responses", "view_func", "result"),
    [
        pytest.param(None, view_func_str, {200: str}, id="generate str 200 response"),
        pytest.param(
            None,
            view_func_pydantic_object,
            {200: Server},
            id="generate object response",
        ),
        pytest.param(
            None, view_func_list, {200: list[Server]}, id="generate list response"
        ),
        pytest.param(
            None,
            view_func_list_dict,
            {200: list[dict[str, Server]]},
            id="generate list dict response",
        ),
        pytest.param(
            {200: list[Server], 202: dict[str, Server]},
            view_func_union,
            {200: list[Server], 202: dict[str, Server]},
            id="Multiple responses - Union return type",
        ),
        pytest.param(
            Server, view_func_pydantic_object, {200: Server}, id="Specified response"
        ),
        pytest.param({"200": str}, view_func_str, {200: str}, id="string return codes"),
    ],
)
def test_sanitize_responses_ok(responses, view_func, result):
    assert Operation._sanitize_responses(responses, view_func) == result


@pytest.mark.parametrize(
    ("responses", "view_func"),
    [
        pytest.param(
            None, view_func_none_return, id="no response specified, no return type"
        ),
        pytest.param(
            {200: list[Server]},
            view_func_union,
            id="Union, not all responses specified",
        ),
        pytest.param({200: int}, view_func_str, id="Wrong response specified"),
    ],
)
def test_sanitize_responses_error(responses, view_func):
    with pytest.raises(ApiConfigError):
        Operation._sanitize_responses(responses, view_func)


@pytest.mark.parametrize(
    ("obj", "result"),
    [
        pytest.param(None, None, id="None"),
        pytest.param(1, 1, id="int"),
        pytest.param("1", "1", id="str"),
        pytest.param([1, 2, 3], [1, 2, 3], id="list[int]"),
        pytest.param({1, 2, 3}, [1, 2, 3], id="set[int]"),
        pytest.param(datetime(2022, 1, 1), "2022-01-01T00:00:00", id="datetime"),
    ],
)
def test_serialize(obj, result):
    assert Operation.serialize(obj) == result


def test_obj_schema():
    operation = Operation("/ping", "GET", view_func_str)
    assert operation._obj_schema(SerializationModel) == {
        "$ref": "#/components/schemas/SerializationModel",
        "title": "ParsingModel[SerializationModel]",
    }
    assert "SerializationModel" in operation.definitions
    assert len(operation.definitions) == 1

    operation.definitions = {}
    # serialize the same object second time, pydantic should not return the same definition again
    assert operation._obj_schema(SerializationModel) == {
        "$ref": "#/components/schemas/SerializationModel",
        "title": "ParsingModel[SerializationModel]",
    }
    assert not operation.definitions


def test_get_schema():
    operation = Operation(
        "/ping",
        "GET",
        view_func_pydantic_object,
        callbacks=[
            Callback(
                name="callback",
                url="someurl",
                method="GET",
                params=[
                    Param(
                        name="get_param",
                        model=int,
                        param_type=ParamType.QUERY,
                        description="Some callback param description",
                    ),
                ],
                request_body=Server,
                response_codes={200: "Success", 500: "Error"},
            )
        ],
        auth=BearerAuth(),
    )

    assert operation.get_schema() == {
        "callbacks": {
            "callback": {
                "someurl": {
                    "get": {
                        "parameters": [
                            {
                                "description": "Some callback param description",
                                "in": "query",
                                "name": "get_param",
                                "required": False,
                                "schema": {"type": "integer"},
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Server",
                                        "title": "ParsingModel[Server]",
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {"description": "Success"},
                            "500": {"description": "Error"},
                        },
                    }
                }
            }
        },
        "description": "Some long description",
        "parameters": [
            {
                "description": "Some int",
                "in": "query",
                "name": "bid",
                "required": False,
                "schema": {"type": "integer"},
            }
        ],
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/Server",
                        "title": "ParsingModel[Server]",
                    }
                }
            }
        },
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/Server",
                            "title": "ParsingModel[Server]",
                        }
                    }
                },
                "description": "",
            }
        },
        "security": [{"bearerTokenAuth": []}],
        "summary": "Some title.",
    }


@pytest.mark.parametrize(
    ("path", "result"),
    [
        (
            "/<any:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"enum": [], "type": "string"},
            },
        ),
        (
            "/<int:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"type": "integer"},
            },
        ),
        (
            "/<int(min=1,max=2):param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"maximum": 2, "minimum": 1, "type": "integer"},
            },
        ),
        (
            "/<float:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"format": "float", "type": "number"},
            },
        ),
        (
            "/<uuid:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"format": "uuid", "type": "string"},
            },
        ),
        (
            "/<path:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"format": "path", "type": "string"},
            },
        ),
        (
            "/<string:param>",
            {
                "description": "",
                "in": "path",
                "name": "param",
                "required": True,
                "schema": {"type": "string"},
            },
        ),
    ],
)
def test_parse_params(path, result):
    def func(param: int) -> str:
        """Some title.

        Some long description

        :param int param: desc param1
        """

    o = Operation(path=path, method="GET", view_func=func)
    assert o._parse_path_params(path, {})["param"].schema == result


def test_parse_multiple_invalid():
    def view_func_invalid(a: list[int], b: list[str]) -> int:
        return 1

    with pytest.raises(ApiConfigError):
        Operation(path="/ping", method="GET", view_func=view_func_invalid)


def test_parse_missing_path_param():
    def view_func_invalid() -> int:
        return 1

    with pytest.raises(ApiConfigError):
        Operation(path="/ping/<int:foo>", method="GET", view_func=view_func_invalid)


def test_parse_complex_path_param():
    def view_func_invalid(foo: Server) -> int:
        return 1

    with pytest.raises(ApiConfigError):
        Operation(path="/ping/<int:foo>", method="GET", view_func=view_func_invalid)


def test_get_openapi_path():
    def view_func_invalid(foo: int) -> int:
        return 1

    o = Operation(path="/ping/<int:foo>", method="GET", view_func=view_func_invalid)
    assert o.get_openapi_path() == "/ping/{foo}"


def test_run(test_app):
    def view_func(foo: int, bar: str, server: Server) -> int:
        return 1

    with test_app.test_request_context(
        json={"url": "some_url", "description": "foo"}, query_string={"foo": 1}
    ):
        o = Operation(path="/ping/<int:bar>", method="GET", view_func=view_func)
        o.view_func = MagicMock(return_value=5)
        o.run(bar=2)

        o.view_func.assert_called_with(
            bar=2, foo=1, server=Server(url="some_url", description="foo")
        )


def test_run_wrong_returned_type(test_app):
    def view_func() -> int:
        return 1

    with pytest.raises(ApiConfigError):
        with test_app.test_request_context():
            o = Operation(path="/ping", method="GET", view_func=view_func)
            o.view_func = MagicMock(return_value="foo")
            o.run()


def test_run_parse_error(test_app):
    def view_func(server: Server) -> int:
        return 1

    with test_app.test_request_context(json={"urll": "some_url"}):
        o = Operation(path="/ping", method="GET", view_func=view_func)
        assert o.run()[1] == 400


def test_run_authorized(test_app):
    def view_func() -> int:
        return 1

    with test_app.test_request_context(headers={"Authorization": "bearer dev"}):
        o = Operation(
            path="/ping", method="GET", view_func=view_func, auth=BearerAuth()
        )
        assert o.run()[1] == 200


def test_run_unauthorized(test_app):
    def view_func() -> int:
        return 1

    with test_app.test_request_context(headers={"Authorization": "bearer dev"}):
        o = Operation(
            path="/ping",
            method="GET",
            view_func=view_func,
            auth=BearerAuthUnauthorized(),
        )
        assert o.run()[1] == 401
