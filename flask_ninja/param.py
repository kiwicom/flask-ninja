from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from werkzeug.routing import parse_converter_args


class ParamType(Enum):
    BODY = "body"
    PATH = "path"
    QUERY = "query"


class Param:
    """Stores one endpoint parameter and its schema."""

    name: str
    model: Any
    param_type: ParamType
    schema: dict

    def __init__(
        self,
        name: str,
        model: Any,
        param_type: ParamType,
        schema: Optional[dict] = None,
        description: str = "",
        required: bool = False,
    ):
        self.name = name
        self.model = model
        self.param_type = param_type
        self.schema = schema or self.default_schema(
            model, param_type, name, description, required
        )

    @classmethod
    def from_path(
        cls, converter: str, arguments: Any, variable: str, param_docs: dict[str, str]
    ) -> Param:
        """Parse flask endpoint param and generate openapi schema for it."""
        args, kwargs = [], {}

        if arguments:
            args, kwargs = parse_converter_args(arguments)

        schema: dict[str, Any] = {}
        if converter == "any":
            schema = {
                "type": "string",
                "enum": args,
            }
        elif converter == "int":
            schema = {
                "type": "integer",
            }
            if "max" in kwargs:
                schema["maximum"] = kwargs["max"]
            if "min" in kwargs:
                schema["minimum"] = kwargs["min"]
        elif converter == "float":
            schema = {
                "type": "number",
                "format": "float",
            }
        elif converter == "uuid":
            schema = {
                "type": "string",
                "format": "uuid",
            }
        elif converter == "path":
            schema = {
                "type": "string",
                "format": "path",
            }
        elif converter == "string":
            schema = {
                "type": "string",
            }
            for prop in ["length", "maxLength", "minLength"]:
                if prop in kwargs:
                    schema[prop] = kwargs[prop]
        elif converter == "default":
            schema = {"type": "string"}

        description = param_docs.get(variable, "")

        return cls(
            name=variable,
            model=int if schema["type"] == "integer" else str,
            param_type=ParamType.PATH,
            schema={
                "name": variable,
                "in": ParamType.PATH.value,
                "required": True,
                "schema": schema,
                "description": description,
            },
        )

    @staticmethod
    def default_schema(
        model: Any, param_type: ParamType, name: str, description: str, required: bool
    ) -> dict:
        return {
            "name": name,
            "in": param_type.value,
            "required": required,
            "schema": {"type": "integer"} if model == int else {"type": "string"},
            "description": description,
        }
