Router
======

Working with Routers
````````````````````

Real world applications can almost never fit all logic into a single file.
Flask Ninja comes with an easy way to split your API into multiple modules using Routers.
A Router is a set of endpoints which can be registered on an application. You can

* add an endpoint to a Router
* register a Router into another Router (using a prefix) - this is helpful if your application has more complex components that doesn't fit into one file - you can build them from even smaller modules
* register a Router on an Flask Ninja application

**Example:**

Let's define two modules `blogs` and `users`

``blogs.py``

.. code-block:: python

    from flask_ninja.router import Router

    api = Router()

    @api.get("/")
    def get_blogs() -> Response:
        ...

    @api.post("/new")
    def create_blog() -> Response:
        ...


``users.py``

.. code-block:: python

    from flask_ninja.router import Router

    api = Router()

    @api.get("/")
    def get_users() -> Response:
        ...

    @api.post("/new")
    def create_user() -> Response:
        ...


Now we register both routers to the API instance with `blogs` and `users` prefixes.

``api.py``

.. code-block:: python

    from flask import Flask
    from flask_ninja import NinjaAPI

    from .blogs import api as blogs_api
    from .users import api as users_api


    app = Flask(__name__)
    api = NinjaAPI(app)

    api.add_router(blogs_api, prefix="/blogs")
    api.add_router(users_api, prefix="/users")


And we can access the following endpoints:

* ``/blogs/``
* ``/blogs/new``
* ``/users/``
* ``/users/new``

**Example 2:** Register a router to a router:

.. code-block:: python

    from flask_ninja import Router

    from .blogs import api as blogs_api
    from .users import api as users_api

    api = Router()

    api.add_router(blogs_api, prefix="/blogs")
    api.add_router(users_api, prefix="/users")

Auth
````

If the endpoints in the router need different authentication than rest of the application, you can set it up by the ``auth`` param. This will set up the authentication for all endpoints and routers attached to this router if they haven't already configured authentication.

.. code-block:: python

    api = Router(auth=BearerAuth())
