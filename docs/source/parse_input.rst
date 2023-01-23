Parse input
===========

One of the flask-ninja features is the automatic parsing or input. Flask-ninja automatically parses:

* path arguments
* query arguments
* headers
* request body

and provides them via the arguments of the function.

Path Parameters
```````````````

You can declare path parameters in the same way as in Flask.

.. code-block:: python

    @api.get("/items/<item_id>")
    def compute(item_id: int) -> Response:
        ...

The value of the path parameter ``item_id`` will be parsed as an int and passed to your function as the argument ``item_id``.

.. note::
    You can add the converter to the path string, but it must match the type annotation of the function argument.

.. code-block:: python

    @api.get("/items/<int:item_id>")
    def compute(item_id: int) -> Response:
        ...

Otherwise an error like this is thrown:

.. code-block:: bash

    flask_ninja.operation.ApiConfigError: Function requires a argument of type integer, got string



Query Parameters
````````````````

Parameters of the function that **are not mentioned in the path** are considered as query parameters, and flask-ninja parses them from the query string.

.. code-block:: python

    @api.get("/items/<item_id>")
    def compute(item_id: int, language: str = "en") -> Response:
        ...

In this case, the ``item_id`` is path parameter, because it is mentioned in the path, and the ``language`` is a query parameter, because it is not mentioned in the path.

.. note::
    If you don't provide the default value for the query parameters, it's also an option, but then you need to always provide the parameters in the query string, otherwise you get an error.


Headers
```````

In order to take a variable from headers, use ``Header`` as a default value.

.. code-block:: python

    from flask_ninja import Header

    @api.get("/items/")
    def compute(item_id: int = Header()) -> Response:
        ...


Request body
````````````

To parse a request body and pass it to your function as an argument, you need to add the argument to your function.

.. code-block:: python

    @api.get("/items/<item_id>")
    def compute(item_id: int, body: RequestBody) -> Response:
        ...

There is a simple rule to decide if an argument of the function is a query argument, or a request body. If the type of the argument is a simple type
e.g. ``int``, ``str``, ``float``, ``bool``, etc... it is considered a query argument. Otherwise if it is a complex type - a ``pydantic`` object, or a ``dict``, ``list`` or ``tuple``, it is considered a request body.

.. note::
    A function can have at most one argument of complex type - since there can be only one request body.
