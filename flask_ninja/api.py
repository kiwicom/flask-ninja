import re
from typing import Any, Callable, Optional

from flask import Blueprint, Flask, render_template
from pydantic import BaseModel

from .constants import NOT_SET
from .router import Router
from .swagger_ui import swagger_ui_path


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
        prefix: str = "",
        docs_url: str = "/docs",
    ):
        swagger_bp = Blueprint(
            "swagger_ui",
            __name__,
            static_url_path="",
            static_folder=swagger_ui_path,
            template_folder=swagger_ui_path,
        )
        swagger_bp.add_url_rule(
            "/",
            "docs",
            lambda: render_template(
                "index.j2", openapi_spec_url=f"{prefix}{docs_url}/openapi.json"
            ),
        )
        swagger_bp.add_url_rule(
            "/openapi.json", "openapi", self.get_schema, methods=["GET"]
        )
        app.register_blueprint(swagger_bp, url_prefix=f"{prefix}{docs_url}")
        self.router = Router(auth=auth, app=app)
        self.title = title
        self.description = description
        self.version = version
        self.servers = servers
        self.prefix = prefix
        self.model_definitions: dict[str, Any] = {}

    def get(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("GET", self.prefix + path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("POST", self.prefix + path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("PUT", self.prefix + path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("PATCH", self.prefix + path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable:
        return self.router.add_route("DELETE", self.prefix + path, **kwargs)

    def add_router(self, router: Router, prefix: str = "") -> None:
        self.router.add_router(router, f"{self.prefix}{prefix}")

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
