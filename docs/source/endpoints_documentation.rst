Documenting your API
==========================

Endpoint documentation
``````````````````````

Writing a documentation for your endpoints is easy and natural. You just simply describe everything in the endpoint function docstring.
Title for your endpoint is taken from the first line of your endpoint, and the description is the text on the next lines.


Arguments documentation
```````````````````````

Documentation for the request body argument and response is taken from the ``pydantic`` model description - as we expect your models are well documented :)
This is a good practice, because it forces you to document the models not only for the response but also everywhere in the code.

For the other arguments, such as path arguments and query arguments, the documentation is taken from the function docstring params.

.. code-block:: python

    class RequestBody(BaseModel):
        """Request body for the foo endpoint."""
        name: str
        age: int

    @api.get("/compute/<a>/")
    def foo(a: int, b: int, body: RequestBody) -> Response:
        """Computes results of various number operations.

        This endpoint returns a result of the following operations:
        - sum
        - difference
        - product
        - power

        :param int a: First number
        :param int b: Second number
        """
        return Response()
