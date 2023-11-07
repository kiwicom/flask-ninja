# pylint: disable=protected-access
import dataclasses
import inspect
from typing import Annotated, Any, Mapping, Optional, Type, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic._internal._utils import lenient_issubclass
from pydantic.fields import FieldInfo

from flask_ninja import param
from flask_ninja.constants import ApiConfigError
from flask_ninja.model_field import ModelField, Required, Undefined, UnionType
from flask_ninja.param import FuncParam

sequence_types = (list, set, tuple)


def create_model_field(
    name: str,
    type_: Type[Any],
    default: Optional[Any] = Undefined,
    field_info: Optional[FieldInfo] = None,
    alias: Optional[str] = None,
) -> ModelField:
    field_info = field_info or FieldInfo(annotation=type_, default=default, alias=alias)

    return ModelField(name=name, field_info=field_info, mode="validation")


def _annotation_is_complex(annotation: Union[Type[Any], None]) -> bool:
    return (
        lenient_issubclass(annotation, (BaseModel, Mapping))
        or _annotation_is_sequence(annotation)
        or dataclasses.is_dataclass(annotation)
    )


def field_annotation_is_complex(annotation: Union[Type[Any], None]) -> bool:
    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        return any(field_annotation_is_complex(arg) for arg in get_args(annotation))

    return (
        _annotation_is_complex(annotation)
        or _annotation_is_complex(origin)
        or hasattr(origin, "__pydantic_core_schema__")
        or hasattr(origin, "__get_pydantic_core_schema__")
    )


def _annotation_is_sequence(annotation: Union[Type[Any], None]) -> bool:
    if lenient_issubclass(annotation, (str, bytes)):
        return False
    return lenient_issubclass(annotation, sequence_types)


def field_annotation_is_scalar(annotation: Any) -> bool:
    # handle Ellipsis here to make tuple[int, ...] work nicely
    return annotation is Ellipsis or not field_annotation_is_complex(annotation)


def is_scalar_field(field: ModelField) -> bool:
    return field_annotation_is_scalar(field.field_info.annotation) and not isinstance(
        field.field_info, param.Body
    )


def field_annotation_is_sequence(annotation: Union[Type[Any], None]) -> bool:
    return _annotation_is_sequence(annotation) or _annotation_is_sequence(
        get_origin(annotation)
    )


def field_annotation_is_scalar_sequence(annotation: Union[Type[Any], None]) -> bool:
    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        at_least_one_scalar_sequence = False
        for arg in get_args(annotation):
            if field_annotation_is_scalar_sequence(arg):
                at_least_one_scalar_sequence = True
                continue
            if not field_annotation_is_scalar(arg):
                return False
        return at_least_one_scalar_sequence
    return field_annotation_is_sequence(annotation) and all(
        field_annotation_is_scalar(sub_annotation)
        for sub_annotation in get_args(annotation)
    )


def is_scalar_sequence_field(field: ModelField) -> bool:
    return field_annotation_is_scalar_sequence(field.field_info.annotation)


def analyze_param(
    *,
    param_name: str,
    annotation: Any,
    value: Any,
    is_path_param: bool,
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

    field_info = None
    type_annotation: Any = Any

    if (
        annotation is not inspect.Signature.empty
        and get_origin(annotation) is Annotated
    ):
        # Handle annotated types
        # We need to extract info from the annotated type
        annotated_args = get_args(annotation)
        type_annotation = annotated_args[0]
        annotations = [arg for arg in annotated_args[1:] if isinstance(arg, FieldInfo)]
        if len(annotations) > 1:
            raise ApiConfigError(
                f"Cannot specify multiple `Annotated` arguments for {param_name!r}"
            )
        next_annotation = next(iter(annotations), None)
        if isinstance(next_annotation, FieldInfo):
            field_info = type(next_annotation).from_annotation(annotation)
            type_annotation = field_info.annotation

    # Handle not annotated types
    elif annotation is not inspect.Signature.empty:
        type_annotation = annotation

    # If the type wasn't annotated or didn't contain any field info annotation
    if field_info is None:
        default_value = (
            value
            if value is not inspect.Signature.empty and not isinstance(value, FieldInfo)
            else Required
        )
        field_info = FieldInfo(annotation=type_annotation)
        if not is_path_param:
            field_info.default = default_value

    # If the type has assigned a default value that is an instance of FuncParam, e.g. Body()
    # we need to merge field info from the type and from the value.
    #
    # It may happen that we have type e.g.
    # Notification = Annotated[Union[SuccessNotification, ErrorNotification], Field(discriminator="result")]
    # and a function
    # def compute(body: Notification = Body(description="Some description")
    #
    # In this case we need to merge the filed infos, otherwise we either lose the information about the discriminator
    # or about the description
    if isinstance(value, FuncParam):
        field_info = value.__class__(
            **(value._attributes_set | field_info._attributes_set)
        )

    # If it wasn't set explicitly, determinite the type of the field, e.g. Query, Body or Path
    # based on the type of the object
    if isinstance(field_info, FieldInfo) and not isinstance(field_info, FuncParam):
        if is_path_param:
            field_info = param.Path(**field_info._attributes_set)
        elif not field_annotation_is_scalar(annotation=type_annotation):
            field_info = param.Body(**field_info._attributes_set)
        else:
            field_info = param.Query(**field_info._attributes_set)

    # Check consistency of the objects
    if is_path_param and not isinstance(field_info, param.Path):
        raise ApiConfigError(
            f"Cannot use `{field_info.__class__.__name__}` for path param {param_name!r}"
        )

    if isinstance(field_info, param.Path) and not field_annotation_is_scalar(
        annotation=field_info.annotation
    ):
        raise ApiConfigError("Path param must be of a simple type.")

    if not field_info.alias and getattr(field_info, "convert_underscores", None):
        alias = param_name.replace("_", "-")
    else:
        alias = field_info.alias or param_name
    field_info.alias = alias

    return ModelField(name=param_name, field_info=field_info, mode="validation")
