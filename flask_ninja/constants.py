# pylint: disable=dangerous-default-value
from enum import Enum
from typing import Any


class NOT_SET:
    def __bool__(self) -> bool:
        return False

    def __copy__(self) -> Any:
        return NOT_SET

    def __deepcopy__(self, memodict: dict = {}) -> Any:
        return NOT_SET


NOT_SET: Any = NOT_SET()  # type:ignore

REF_PREFIX = "#/components/schemas/"


class ParamType(Enum):
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"
    BODY = "body"


class ApiConfigError(Exception):
    """There is a mistake in the API configuration."""
