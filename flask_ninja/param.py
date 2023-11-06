from __future__ import annotations

from typing import Any, List, Optional

from pydantic.fields import FieldInfo

from flask_ninja.constants import ParamType
from flask_ninja.model_field import Undefined


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
        examples: Optional[List[Any]] = None,
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
        examples: Optional[List[Any]] = None,
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
        examples: Optional[List[Any]] = None,
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
        examples: Optional[List[Any]] = None,
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
        examples: Optional[List[Any]] = None,
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


class Body(FuncParam):
    in_ = ParamType.BODY

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
        examples: Optional[List[Any]] = None,
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"
