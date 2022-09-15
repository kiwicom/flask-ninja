Endpoint operations
===================

Operations
----------

Flask-ninja supports operations for the following http methods:

* GET
* POST
* PUT
* PATCH
* DELETE

.. code-block:: python

    @api.get("/path")
    def get_operation() -> Response:
        ...

    @api.post("/path")
    def post_operation() -> Response:
        ...

    @api.put("/path")
    def put_operation() -> Response:
        ...

    @api.patch("/path")
    def patch_operation() -> Response:
        ...

    @api.delete("/path")
    def delete_operation() -> Response:
        ...


Operation parameters
--------------------
Each operation has the following optional arguments:

Responses
~~~~~~~~~

By default it is assumed that the endpoint respond with 200 response code and returns the model specified as the return type of the function.
However, if the endpoint success response code is different than 200, you can set it via the response argument:

.. code-block:: python

    @api.get("/path", responses={202: Response})
    def get_operation() -> Response:
        ...


If the endpoint returns different responses for different response codes, you can also specify it:

.. code-block:: python

    @api.get("/path", responses={200: Response, 201: CreatedResponse})
    def get_operation() -> Union[Response, CreatedResponse]:
        ...

Only don't forget to mention all responses in the response type annotations. The returned model is then automatically matched with the associated response code.

Callbacks
~~~~~~~~~

If your endpoint access a callback after it is finished, you can specify it.

.. code-block:: python

    @api.get("/path", callbacks=[
            Callback(
                name="Callback name",
                url="{$request.body#/callback_url}",
                method="POST",
                request_body=CallbackRequestBody,
                response_codes={
                    200: "Your server returns this code if it accepts the callback"
                },
            )
        ],
    )
    def get_operation(body: RequestBody) -> Response:
        ...


Summary
~~~~~~~~~~~

The summary is by default parsed from the docstring of the function. However if you for some reason prefer setting it manually,
you can do it via the ``summary`` argument.


Description
~~~~~~~~~~~

The description is by default parsed from the docstring of the function. However if you for some reason prefer setting it manually,
you can do it via the ``description`` argument.

Auth
~~~~~~~~~~~

If the endpoint needs a different authentication than has the router or the whole API, you can set it via the ``auth`` argument.

.. code-block:: python

    @api.get("/path", auth=BearerAuth())
    def get_operation() -> Response:
        ...
