# Flask Ninja

**Flask Ninja** is a web framework for building APIs with Flask and Python 3.9+ type hints.

Key features:

- Easy: Designed to be easy to use and intuitive.
- Fast to code: Type hints and automatic docs lets you focus only on business logic.
- Standards-based: Based on the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.
- Models based: Pydantic models support and automatic (de)serialization of requests/responses.
- Secure: Natively supports various authentication methods for the requests.

## Installation

```
pip install flask-ninja
```

## Usage

In your flask project where you create flask app:

```Python
from flask import Flask
from flask_ninja import NinjaAPI
from pydantic import BaseModel

app = Flask(__name__)
api = NinjaAPI(app)

class Response(BaseModel):
    """Response model containing results of various number operations."""
    sum: int
    difference: int
    product: int
    power: int

@api.get("/compute")
def compute(a: int, b: int) -> Response:
    """Computes results of various number operations.

    This endpoint returns a result of the following operations:
    - sum
    - difference
    - product
    - power

    :param int a: First number
    :param int b: Second number number
    """
    return Response(
        sum=a + b,
        difference=a - b,
        product=a * b,
        power=a ** b
    )

if __name__ == "__main__":
    app.run()
```

**That's it !**

Now you've just created an API that:

- receives an HTTP GET request at `/compute`
- takes, validates and type-casts GET parameters `a` and `b`
- validates the returned Response object and serializes it into JSON
- generates an OpenAPI schema for defined operation

### Interactive API docs

Now go to <a href="http://127.0.0.1:8000/docs" target="_blank">http://127.0.0.1:5000/docs</a>

You will see the automatic interactive API documentation (provided by <a href="https://github.com/swagger-api/swagger-ui" target="_blank">Swagger UI</a>):
