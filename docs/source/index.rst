Flask-Ninja
===================================

**Flask-Ninja** is a simple web API framework based on Flask.
It uses Pydantic for validation and automatic generation of Openapi documentation. It's heavily inspired by `django-ninja <https://django-ninja.rest-framework.com/>`__ framework.

The key features are:
`````````````````````

* **Easy:** Designed to be easy to use and intuitive.
* **Fast to code:** Type hints and automatic docs lets you focus only on business logic.
* **Standards-based:** Based on the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.
* **Models based:** `Pydantic <https://github.com/samuelcolvin/pydantic>`__ models support and automatic (de)serialization of requests/responses.
* **Secure: Natively** supports various authentication methods for the requests.

Motivation
``````````

There is plenty of similar libraries, but each of them is something missing:
 * `flask-openapi3 <https://luolingchun.github.io/flask-openapi3/>`__ - can't return a pydantic model, only a dict
 * `flask-pydantic <https://pypi.org/project/Flask-Pydantic/>`__ - doesn't generate openapi schema
 * `spectree <https://github.com/0b01001001/spectree>`__ - doesn't support authentication

Additional features
```````````````````
* parses docstrings of the endpoint handler function and use them for documenting the endpoint in the generated documentation.
* detects response schema from the return type annotation



Contents
--------

.. toctree::

    getting_started
    api_configuration
    router
    endpoints
    parse_input
    endpoints_documentation
