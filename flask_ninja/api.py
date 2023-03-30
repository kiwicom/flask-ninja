import json
import re
from typing import Any, Callable, Optional

from flask import Blueprint, Flask, render_template
from pydantic.schema import get_flat_models_from_fields, get_model_name_map

from .constants import NOT_SET
from .models import Components, Info, OpenAPI, Server
from .router import Router
from .swagger_ui import swagger_ui_path
from .utils import get_model_definitions


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

    def get_schema(self) -> str:
        """Creates OpenAPI schema for the API."""

        # At first we collect all pydantic models used anywhere
        # in the endpoints - parameters, responses, request bodies, callbacks...
        models = []
        for operation in self.router.operations:
            models += operation.get_models()

        # Then we create from them flat models - it means we extract the models from Generics
        flat_models = get_flat_models_from_fields(models, known_models=set())
        # Then we generate unique names for them - if there are two models from different modules
        # but with the same name, we need provide different names for them in the Definitions list
        model_name_map = get_model_name_map(flat_models)
        paths: dict = {}
        security_schemes: dict = {}
        # Create OpenAPI schemas for all models
        definitions = get_model_definitions(
            flat_models=flat_models, model_name_map=model_name_map
        )

        # Create OpenAPI schema for all operations
        for operation in self.router.operations:
            # Arguments in paths has format e.g. <int:id> in flask which is different than in openapi e.g. {id}
            # therefore we need to convert it to openapi format
            swagger_path = operation.get_openapi_path()
            if swagger_path not in paths:
                paths[swagger_path] = {}
            paths[swagger_path][operation.method.lower()] = operation.get_schema(
                model_name_map=model_name_map
            )
            if operation.auth:
                security_schemes.update(operation.auth.schema())

        schema = OpenAPI(
            openapi=self.OPENAPI_VERSION,
            info=Info(
                title=self.title,
                description=re.sub(r"\n *", "\n", self.description),
                version=self.version,
            ),
            components=Components(
                schemas=definitions, securitySchemes=security_schemes
            ),
            paths=paths,
            servers=self.servers or None,
        )

        return json.loads(schema.json(by_alias=True, exclude_none=True))
