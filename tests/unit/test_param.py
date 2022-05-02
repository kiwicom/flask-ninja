from pydantic import schema_json_of

from flask_ninja.api import Server
from flask_ninja.param import Param, ParamType


def test_param_with_schema():
    param = Param("param", int, param_type=ParamType.QUERY, schema={"key": "value"})
    assert param.name == "param"
    assert param.model == int
    assert param.param_type == ParamType.QUERY
    assert param.schema == {"key": "value"}


def test_param_without_schema():
    param = Param(
        "param",
        int,
        param_type=ParamType.QUERY,
        description="some description",
        required=True,
    )
    assert param.name == "param"
    assert param.model == int
    assert param.param_type == ParamType.QUERY
    assert param.schema == {
        "description": "some description",
        "in": "query",
        "name": "param",
        "required": True,
        "schema": {"type": "integer"},
    }


def test_param_defaults():
    param = Param("param", int, param_type=ParamType.QUERY)
    assert param.name == "param"
    assert param.model == int
    assert param.param_type == ParamType.QUERY
    assert param.schema == {
        "description": "",
        "in": "query",
        "name": "param",
        "required": False,
        "schema": {"type": "integer"},
    }


def test_param_defaults_int():
    param = Param("param", int, param_type=ParamType.QUERY)
    assert param.schema["schema"]["type"] == "integer"


def test_param_defaults_str():
    param = Param("param", str, param_type=ParamType.QUERY)
    assert param.schema["schema"]["type"] == "string"


def test_etc_schema():
    print(schema_json_of(Server))
