# pylint:disable=comparison-with-callable
import json
from typing import Any, Callable, Optional, Tuple, Union, get_origin

from docstring_parser import parse as doc_parse
from flask import jsonify, request
from pydantic import BaseModel, ValidationError, parse_obj_as, schema_of
from werkzeug.routing import parse_rule

from .constants import NOT_SET
from .param import Param, ParamType
from .security import HttpAuthBase


class ApiConfigError(Exception):
    """There is a mistake in the API configuration."""


class Callback(BaseModel):
    name: str
    url: str
    method: str
    request_body: Optional[Any]
    params: Optional[list[Param]]
    response_codes: dict[int, str]

    class Config:
        arbitrary_types_allowed = True


class SerializationModel(BaseModel):
    data: Any

    class Config:
        arbitrary_types_allowed = True


class Operation:
    """Operation represents handler for one endpoint."""

    def __init__(
        self,
        path: str,
        method: str,
        view_func: Callable,
        responses: Optional[Any] = None,
        callbacks: Optional[list[Callback]] = None,
        summary: str = "",
        description: str = "",
        params: Optional[dict[str, Param]] = None,
        auth: Any = NOT_SET,
    ):
        self.path = path
        self.method = method
        self.view_func = view_func
        self.definitions: dict = {}
        self.responses = self._sanitize_responses(responses, self.view_func)
        self.callbacks = callbacks
        self.summary = summary
        self.description = description
        self.auth = auth
        self.params = params or self._parse_params(path)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        # Run authentication if configured
        if self.auth and self.auth() is None:
            return jsonify("Unauthorized"), 401

        try:
            for param_name, param in self.params.items():
                # Parse query params
                if param.param_type == ParamType.QUERY and param_name in request.args:
                    kwargs[param_name] = parse_obj_as(
                        param.model, request.args[param_name]
                    )
                # Parse request body
                elif param.param_type == ParamType.BODY:
                    kwargs[param_name] = parse_obj_as(param.model, request.json)
        except ValidationError as validation_error:
            return validation_error.json(), 400

        # Run the original view function
        resp = self.view_func(*args, **kwargs)

        # Find model and response code for the returned object
        for code, model in self.responses.items():
            # if the mode is some generic with specified type
            # e.g. list[str], dict[str, Response], etc, we can't use isinstance and
            # at first need to get the unspecified generic type - e.g. list, dict, etc
            # TODO match also the inner types of generics - but that's a corner case
            if isinstance(resp, get_origin(model) or model):
                return jsonify(self.serialize(resp)), code

        raise ApiConfigError(f"No response schema matches returned type {type(resp)}")

    @staticmethod
    def _sanitize_responses(responses: Any, view_func: Callable) -> dict[int, Any]:
        func_return_type = view_func.__annotations__.get("return")

        # Return code not specified, setting it to 200
        if not isinstance(responses, dict):
            responses = {200: responses} if responses else {}
        else:
            # convert all response codes to ints
            responses = {int(k): v for k, v in responses.items()}

        # If responses weren't specified, try to generate it from return type
        if not responses:
            # It can't be an Union
            if func_return_type is None or get_origin(func_return_type) == Union:
                raise ApiConfigError("Return type not specified.")
            responses[200] = func_return_type

        # Check if for each returned type there is implicitly or explicitly defined response model and code
        if func_return_type:
            if get_origin(func_return_type) == Union:
                for ret_type in func_return_type.__args__:
                    if ret_type not in responses.values():
                        raise ApiConfigError(
                            f"Return type {ret_type} http code must be specified explicitly."
                        )

            # If we specified different return type as we specified as response
            elif 200 in responses and responses[200] != func_return_type:
                raise ApiConfigError(
                    f"Return type of the function {type(func_return_type)} does not match response type {type(responses[200])}"
                )
        return responses

    @classmethod
    def serialize(cls, resp: Any) -> Any:
        """Convert response object into json serializable object.

        TODO: Avoid json serialization and deserialization.
        """
        return json.loads(SerializationModel(data=resp).json())["data"]

    def _obj_schema(self, obj: Any) -> dict:
        """Generate schema for a model using pydantic and store definitions."""
        schema = schema_of(obj, ref_template="#/components/schemas/{model}")
        self.definitions.update(schema.get("definitions", {}))

        if "definitions" in schema:
            del schema["definitions"]

        return schema

    def get_callback_schema(self, cb: Callback) -> dict:
        schema: dict = {}
        if cb.request_body:
            schema["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {"schema": self._obj_schema(cb.request_body)}
                },
            }
        if cb.params:
            schema["parameters"] = [param.schema for param in cb.params]

        if cb.response_codes:
            schema["responses"] = {
                str(code): {"description": description}
                for code, description in cb.response_codes.items()
            }

        return {cb.url: {cb.method.lower(): schema}}

    def get_schema(self) -> dict:
        """Generate schema for the operation."""
        doc = doc_parse(self.view_func.__doc__ or "")

        operation_schema: dict[str, Any] = {
            "summary": doc.short_description or self.summary,
            "description": doc.long_description or self.description,
            "responses": {},
        }

        for code, response in self.responses.items():
            schema = self._obj_schema(response)
            operation_schema["responses"][str(code)] = {
                "content": {"application/json": {"schema": schema}},
                "description": "",
            }

        parameters = []

        for param in self.params.values():
            if param.param_type == ParamType.BODY:
                operation_schema["requestBody"] = {
                    "content": {"application/json": {"schema": param.schema}}
                }
            else:
                parameters.append(param.schema)

        if self.auth:
            operation_schema["security"] = [{self.auth.schema_name: []}]

        if parameters:
            operation_schema["parameters"] = parameters

        if self.callbacks:
            callback_schema = {}
            for callback in self.callbacks:
                callback_schema[callback.name] = self.get_callback_schema(callback)
            operation_schema["callbacks"] = callback_schema

        return operation_schema

    def _parse_path_params(
        self, path: str, param_docs: dict[str, str]
    ) -> dict[str, Param]:
        """Parse path params from endpoint path."""
        return {
            variable: Param.from_path(converter, arguments, variable, param_docs)
            for converter, arguments, variable in parse_rule(path)
            if converter is not None
        }

    def _parse_func_params(
        self, param_docs: dict[str, str]
    ) -> Tuple[dict[str, Param], dict[str, Param]]:
        """Parse query and body params from function arguments."""
        body_params = {}
        query_params = {}
        for param_name, param in self.view_func.__annotations__.items():
            if param_name == "return":
                continue
            if get_origin(param) in (list, dict, tuple) or issubclass(param, BaseModel):
                body_params[param_name] = Param(
                    name=param_name,
                    model=param,
                    param_type=ParamType.BODY,
                    schema=self._obj_schema(param),
                )
            else:
                mapper = {str: "string", int: "integer"}

                query_params[param_name] = Param(
                    name=param_name,
                    model=param,
                    param_type=ParamType.QUERY,
                    schema={
                        "name": param_name,
                        "in": ParamType.QUERY.value,
                        "required": False,
                        "schema": {
                            "type": mapper[param],
                        },
                        "description": param_docs.get(param_name, ""),
                    },
                )

        return query_params, body_params

    def _parse_params(self, path: str) -> dict[str, Param]:
        """Parse path, query and body params from endpoint path and function arguments.

        The idea is:
        - if a param is in endpoint path string - it is a path param
        - if it's not and it's a complex type - list, dict, object - it is body param
        - otherwise it is query param
        """
        param_docs = {
            param.arg_name: param.description or ""
            for param in doc_parse(self.view_func.__doc__ or "").params
        }

        path_params = self._parse_path_params(path, param_docs)
        query_params, body_params = self._parse_func_params(param_docs)

        for param in path_params:
            # We recognized the param as path param, not query param
            if param in query_params:
                del query_params[param]
            elif param in body_params:
                raise ApiConfigError(
                    f"Param of type {type(body_params[param])} can't be path param."
                )
            else:
                raise ApiConfigError(f"Function is missing {param} argument")

        if len(body_params) > 1:
            raise ApiConfigError("Multiple complex objects in function arguments.")

        return path_params | query_params | body_params

    def get_openapi_path(self) -> str:
        """Convert flask endpoint path into openapi path."""
        subs = []

        for converter, _, variable in parse_rule(self.path):
            if converter is None:
                subs.append(variable)
                continue
            subs.append(f"{{{variable}}}")
        return "".join(subs)

    def add_prefix(self, prefix: str) -> None:
        self.path = prefix + self.path

    def update_auth(self, auth: Optional[HttpAuthBase] = None) -> None:
        self.auth = self.auth if self.auth != NOT_SET else auth
