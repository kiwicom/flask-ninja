# pylint: disable=protected-access, unused-argument,disallowed-name
import json
from datetime import datetime
from typing import Mapping, Union
from unittest.mock import MagicMock

import pytest
from pydantic.schema import get_flat_models_from_fields, get_model_name_map
from werkzeug.datastructures import MultiDict

from flask_ninja import Header, Query
from flask_ninja.api import Server
from flask_ninja.operation import ApiConfigError, Callback, Operation
from flask_ninja.utils import create_model_field
from tests.conftest import BearerAuth, BearerAuthUnauthorized


def view_func_str() -> str:
    return ""


def view_func_pydantic_object(bid: int, server: Server) -> Server:
    """Some title.

    Some long description

    :param int bid: Some int
    :param Server server: Some server
    """
    return Server(url=str(bid), description=server.description)  # some return value


def view_func_list() -> list[Server]:
    return []


def view_func_list_dict() -> list[dict[str, Server]]:
    return []


def view_func_union() -> Union[list[Server], dict[str, Server]]:
    return []


def view_func_none_return() -> None:
    return None


@pytest.mark.parametrize(
    ("responses", "view_func", "result"),
    [
        pytest.param(
            None,
            view_func_str,
            {200: create_model_field(name="Response 200", type_=str, required=True)},
            id="generate str 200 response",
        ),
        pytest.param(
            None,
            view_func_pydantic_object,
            {200: create_model_field(name="Response 200", type_=Server, required=True)},
            id="generate object response",
        ),
        pytest.param(
            None,
            view_func_list,
            {
                200: create_model_field(
                    name="Response 200", type_=list[Server], required=True
                )
            },
            id="generate list response",
        ),
        pytest.param(
            None,
            view_func_list_dict,
            {
                200: create_model_field(
                    name="Response 200", type_=list[dict[str, Server]], required=True
                )
            },
            id="generate list dict response",
        ),
        pytest.param(
            {200: list[Server], 202: dict[str, Server]},
            view_func_union,
            {
                200: create_model_field(
                    name="Response 200", type_=list[Server], required=True
                ),
                202: create_model_field(
                    name="Response 202", type_=Mapping[str, Server], required=True
                ),
            },
            id="Multiple responses - Union return type",
        ),
        pytest.param(
            Server,
            view_func_pydantic_object,
            {200: create_model_field(name="Response 200", type_=Server, required=True)},
            id="Specified response",
        ),
        pytest.param(
            {"200": str},
            view_func_str,
            {200: create_model_field(name="Response 200", type_=str, required=True)},
            id="string return codes",
        ),
    ],
)
def test_sanitize_responses_ok(responses, view_func, result):
    assert str(Operation._sanitize_responses(responses, view_func)) == str(result)


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
                    create_model_field(
                        name="get_param",
                        type_=int,
                        field_info=Query(description="Some callback param description"),
                    ),
                ],
                request_body=Server,
                response_codes={200: "Success", 500: "Error"},
            )
        ],
        auth=BearerAuth(),
    )

    models = operation.get_models()
    flat_models = get_flat_models_from_fields(models, known_models=set())
    model_name_map = get_model_name_map(flat_models)

    assert operation.get_schema(model_name_map=model_name_map).json(
        by_alias=True, exclude_none=True
    ) == json.dumps(
        {
            "summary": "Some title.",
            "description": "Some long description",
            "parameters": [
                {
                    "description": "Some int",
                    "required": True,
                    "schema": {
                        "title": "Bid",
                        "type": "integer",
                        "description": "Some int",
                    },
                    "name": "bid",
                    "in": "query",
                }
            ],
            "requestBody": {
                "description": "",
                "content": {
                    "application/json": {
                        "schema": {
                            "title": "Server",
                            "allOf": [{"$ref": "#/components/schemas/Server"}],
                            "description": "Some server",
                        }
                    }
                },
                "required": True,
            },
            "responses": {
                "200": {
                    "description": "",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Server"}
                        }
                    },
                }
            },
            "callbacks": {
                "callback": {
                    "someurl": {
                        "get": {
                            "parameters": [
                                {
                                    "description": "Some callback param description",
                                    "required": True,
                                    "schema": {
                                        "title": "Get Param",
                                        "type": "integer",
                                        "description": "Some callback param description",
                                    },
                                    "name": "get_param",
                                    "in": "query",
                                }
                            ],
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Server"
                                        }
                                    }
                                },
                                "required": True,
                            },
                            "responses": {
                                "200": {"description": "Success"},
                                "500": {"description": "Error"},
                            },
                        }
                    }
                }
            },
            "security": [{"bearerTokenAuth": []}],
        }
    )


@pytest.mark.parametrize(
    ("path", "result"),
    [
        ("/<any:param>", ["param"]),
        ("/<int:param>", ["param"]),
        ("/<int(min=1,max=2):param>", ["param"]),
        ("/<float:param>", ["param"]),
        ("/<uuid:param>", ["param"]),
        ("/<path:param>", ["param"]),
        ("/<string:param>", ["param"]),
        ("/<string:param>/<int:param1>", ["param", "param1"]),
    ],
)
def test_parse_params(path, result):
    def func(param: int, param1: int) -> str:
        """Some title.

        Some long description

        :param int param: desc param1
        """
        return ""

    o = Operation(path=path, method="GET", view_func=func)
    assert o._parse_path_params(path) == result


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
    def view_func(
        foo: int, bar: str, server: Server, header_param: int = Header()
    ) -> int:
        return 1

    with test_app.test_request_context(
        json={"url": "some_url", "description": "foo"},
        query_string={"foo": 1},
        headers={"header-param": 10},
    ):
        o = Operation(path="/ping/<string:bar>", method="GET", view_func=view_func)
        o.view_func = MagicMock(return_value=5)
        o.run(bar=2)

        o.view_func.assert_called_with(
            bar=2,
            foo=1,
            server=Server(url="some_url", description="foo"),
            header_param=10,
        )


def test_run_query_list(test_app):
    def view_func(foo: list[int] = Query(), bar: list[str] = Query()) -> int:
        return 1

    with test_app.test_request_context(
        query_string=MultiDict([("foo", 1), ("foo", 2), ("bar", "a"), ("bar", "b")]),
    ):
        o = Operation(path="/ping", method="GET", view_func=view_func)
        o.view_func = MagicMock(return_value=5)
        o.run()

        o.view_func.assert_called_with(
            bar=["a", "b"],
            foo=[1, 2],
        )


def test_run_generics(test_app):
    def view_func(items: list[int]) -> list[int]:
        return items

    with test_app.test_request_context(
        json=[1, 2, 3],
    ):
        o = Operation(path="/ping/", method="POST", view_func=view_func)
        assert o.run()[0].json == [1, 2, 3]


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
