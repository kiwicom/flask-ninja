import dataclasses
import inspect
from enum import Enum
from typing import Any, Dict, Optional, Set, Type, Union

from pydantic import BaseConfig, BaseModel
from pydantic.class_validators import Validator
from pydantic.fields import (
    SHAPE_SINGLETON,
    FieldInfo,
    ModelField,
    Required,
    Undefined,
    UndefinedType,
)
from pydantic.schema import model_process_schema
from pydantic.utils import lenient_issubclass

from flask_ninja.constants import REF_PREFIX, ApiConfigError
from flask_ninja.param import FuncParam, ParamType

sequence_types = (list, set, tuple)


def create_model_field(
    name: str,
    type_: Type[Any],
    class_validators: Optional[Dict[str, Validator]] = None,
    default: Optional[Any] = None,
    required: Union[bool, UndefinedType] = True,
    model_config: Type[BaseConfig] = BaseConfig,
    field_info: Optional[FieldInfo] = None,
    alias: Optional[str] = None,
) -> ModelField:
    class_validators = class_validators or {}
    field_info = field_info or FieldInfo()

    return ModelField(
        name=name,
        type_=type_,
        class_validators=class_validators,
        default=default,
        required=required,
        model_config=model_config,
        alias=alias,
        field_info=field_info,
    )


def is_scalar_field(field: ModelField) -> bool:
    if (
        field.shape != SHAPE_SINGLETON
        or lenient_issubclass(field.type_, BaseModel)
        or lenient_issubclass(field.type_, sequence_types + (dict,))
        or dataclasses.is_dataclass(field.type_)
    ):
        return False

    if field.sub_fields:
        if not all(is_scalar_field(f) for f in field.sub_fields):
            return False

    return True


def get_model_definitions(
    flat_models: Set[Union[Type[BaseModel], Type[Enum]]],
    model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
) -> Dict[str, Any]:
    definitions: Dict[str, Dict[str, Any]] = {}
    for model in flat_models:
        m_schema, m_definitions, _ = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=REF_PREFIX
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        if "description" in m_schema:
            m_schema["description"] = m_schema["description"].split("\f")[0]
        definitions[model_name] = m_schema

    return definitions


def get_param_model_field(
    *,
    param: inspect.Parameter,
    default_field_info: Type[FuncParam] = FuncParam,
    force_type: Optional[ParamType] = None,
    ignore_default: bool = False,
) -> ModelField:
    """Converts inspected parameter into pydantic ModelField object.

    We provide additional argument info as its default value.

    Example:
    def foo(arg:int = Header(description="Sample")):

    In this case we retrieve via inspect the object Header(description="Sample")
    The object is of the type FieldInfo, so it contains all necessary attributes.

    Then we combine it with the annotation info - argument name, type, etc.
    and create a Model field containing all the information about the parameter.
    """
    default_value: Any = Undefined

    if not param.default == param.empty and ignore_default is False:
        default_value = param.default
    if isinstance(default_value, FieldInfo):
        field_info = default_value
        default_value = field_info.default
        if (
            isinstance(field_info, FuncParam)
            and getattr(field_info, "in_", None) is None
        ):
            field_info.in_ = default_field_info.in_
    else:
        field_info = default_field_info(default=default_value)

    if force_type:
        field_info.in_ = force_type  # type: ignore

    required = True
    if default_value is Required or ignore_default:
        required = True
        default_value = None
    elif default_value is not Undefined:
        required = False

    if not field_info.alias and getattr(field_info, "convert_underscores", None):
        alias = param.name.replace("_", "-")
    else:
        alias = field_info.alias or param.name

    field = ModelField(
        name=param.name,
        type_=param.annotation,
        default=default_value,
        alias=alias,
        required=required,
        field_info=field_info,
        class_validators={},
        model_config=BaseConfig,
    )

    if getattr(field.field_info, "in_", None) is None:
        if is_scalar_field(field):
            field.field_info.in_ = ParamType.QUERY  # type:ignore
        else:
            field.field_info.in_ = ParamType.BODY  # type:ignore

    if field.field_info.in_ != ParamType.BODY and not is_scalar_field(  # type:ignore
        field
    ):
        raise ApiConfigError("Path param must be of a simple type.")

    return field
