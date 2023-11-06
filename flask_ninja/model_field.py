import types
from dataclasses import dataclass
from typing import Annotated, Any, Dict, List, Literal, Sequence, Set, Tuple, Union

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import PydanticUndefined, PydanticUndefinedType

Required = PydanticUndefined
Undefined = PydanticUndefined
UndefinedType = PydanticUndefinedType
IncEx = Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any]]
UnionType = getattr(types, "UnionType", Union)


@dataclass
class ModelField:
    field_info: FieldInfo
    name: str
    mode: Literal["validation", "serialization"] = "validation"

    @property
    def alias(self) -> str:
        a = self.field_info.alias
        return a if a is not None else self.name

    @property
    def required(self) -> bool:
        return self.field_info.is_required()

    @property
    def default(self) -> Any:
        return self.get_default()

    @property
    def type_(self) -> Any:
        return self.field_info.annotation

    def __post_init__(self) -> None:
        self.type_adapter: TypeAdapter[Any] = TypeAdapter(
            Annotated[self.field_info.annotation, self.field_info]
        )

    def get_default(self) -> Any:
        if self.field_info.is_required():
            return Undefined
        return self.field_info.get_default(call_default_factory=True)

    def __hash__(self) -> int:
        # Each ModelField is unique for our purposes, to allow making a dict from
        # ModelField to its JSON Schema.
        return id(self)


def _regenerate_error_with_loc(
    *, errors: Sequence[Any], loc_prefix: Tuple[Union[str, int], ...]
) -> List[Dict[str, Any]]:
    updated_loc_errors: List[Any] = [
        {**err, "loc": loc_prefix + err.get("loc", ())} for err in errors
    ]

    return updated_loc_errors


FieldMapping = Dict[
    tuple[ModelField, Literal["validation", "serialization"]], JsonSchemaValue
]
