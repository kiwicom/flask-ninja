import abc
from typing import Any, Optional

from flask import request


class HttpAuthBase(abc.ABC):
    openapi_type: str = "http"
    schema_name: str

    @abc.abstractmethod
    def __call__(self) -> Optional[Any]:
        pass  # pragma: no cover

    @abc.abstractmethod
    def schema(self) -> dict:
        pass


class HttpBearer(HttpAuthBase, abc.ABC):

    schema_name: str = "bearerTokenAuth"
    openapi_scheme: str = "bearer"
    header: str = "Authorization"

    def __call__(self) -> Optional[Any]:

        auth_value = request.headers.get(self.header)
        if not auth_value:
            return None
        parts = auth_value.split(" ")

        if parts[0].lower() != self.openapi_scheme:
            return None
        token = " ".join(parts[1:])
        return self.authenticate(token)

    @abc.abstractmethod
    def authenticate(self, token: str) -> Optional[Any]:
        pass  # pragma: no cover

    def schema(self) -> dict:
        return {
            self.schema_name: {"scheme": self.openapi_scheme, "type": self.openapi_type}
        }
