# pylint: disable=dangerous-default-value
from typing import Any


class NOT_SET:
    def __bool__(self) -> bool:
        return False

    def __copy__(self) -> Any:
        return NOT_SET

    def __deepcopy__(self, memodict: dict = {}) -> Any:
        return NOT_SET


NOT_SET: Any = NOT_SET()  # type:ignore
