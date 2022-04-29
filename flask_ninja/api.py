import re
from typing import Any, Callable, Optional

from flask import Flask
from pydantic import BaseModel

from .constants import NOT_SET
from .page import HTML
from .router import Router


class Server(BaseModel):
    url: str
    description: str


class NinjaAPI:
    OPENAPI_VERSION = "3.0.3"

    def __init__(
        self,
        app: Flask,
        auth: Any = NOT_SET,
        title: str = "",
        description: str = "",
        version: str = "1.0.0",
        servers: Optional[list[Server]] = None,
    ):
        app.add_url_rule("/docs", "docs", self.get_docs, methods=["GET"])
        app.add_url_rule("/openapi.json", "openapi", self.get_schema, methods=["GET"])
        self.router = Router(auth=auth, app=app)
        self.title = title
        self.description = description
        self.version = version
        self.servers = servers
        self.model_definitions: dict[str, Any] = {}

    def get(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("DELETE", path, **kwargs)

    def add_router(self, router: Router, prefix: str = "") -> None:
        self.router.add_router(router, prefix)

    def get_schema(self) -> dict:
        """Generate Openapi schema for the API."""

        paths: dict = {}
        security_schemes: dict = {}

        for operation in self.router.operations:
            # Arguments in paths has format e.g. <int:id> in flask which is different than in openapi e.g. {id}
            # therefore we need to convert it to openapi format
            swagger_path = operation.get_openapi_path()
            if swagger_path not in paths:
                paths[swagger_path] = {}
            paths[swagger_path][operation.method.lower()] = operation.get_schema()

            # Pydantic somehow caches generated definitions and second time a schema is generated for a model
            # only a reference is returned. Therefore we need to carefully store the generated definitions
            # to be able to provide them in the response.
            self.model_definitions.update(operation.definitions)

            if operation.auth:
                security_schemes.update(operation.auth.schema())

        schema: dict = {
            "openapi": self.OPENAPI_VERSION,
            "info": {
                "title": self.title,
                # strip whitespaces in the beginning of lines caused by indents
                "description": re.sub(r"\n *", "\n", self.description),
                "version": self.version,
            },
            "components": {
                "schemas": self.model_definitions,
                "securitySchemes": security_schemes,
            },
            "paths": paths,
        }
        if self.servers:
            schema["servers"] = [server.dict() for server in self.servers]

        return schema

    def get_docs(self) -> str:
        return HTML.format(
            spec_url="/openapi.json",
            spec_path="/openapi.json",
            client_id="",
            client_secret="",
            realm="",
            app_name=self.title,
            scope_separator=" ",
            additional_query_string_params={},
            use_basic_authentication_with_access_code_grant=False,
            use_pkce_with_authorization_code_grant=False,
        )
