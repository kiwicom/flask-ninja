from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic.fields import FieldInfo, Undefined
from werkzeug.routing import parse_converter_args


class ParamType(Enum):
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"
    BODY = "body"


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
            schema = {"type": None}

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


class FuncParam(FieldInfo):
    in_: ParamType

    def __init__(
        self,
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        self.deprecated = deprecated
        self.example = example
        self.examples = examples
        self.include_in_schema = include_in_schema
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            **extra,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"


class Path(FuncParam):
    in_ = ParamType.PATH

    def __init__(
        self,
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        self.in_ = self.in_
        super().__init__(
            default=...,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )


class Query(FuncParam):
    in_ = ParamType.QUERY

    def __init__(
        self,
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )


class Header(FuncParam):
    in_ = ParamType.HEADER

    def __init__(
        self,
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        convert_underscores: bool = True,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        self.convert_underscores = convert_underscores
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )


class Cookie(FuncParam):
    in_ = ParamType.COOKIE

    def __init__(
        self,
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
    ):
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            deprecated=deprecated,
            example=example,
            examples=examples,
            include_in_schema=include_in_schema,
            **extra,
        )


class Body(FieldInfo):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        embed: bool = False,
        media_type: str = "application/json",
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        **extra: Any,
    ):
        self.embed = embed
        self.media_type = media_type
        self.example = example
        self.examples = examples
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            **extra,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"
