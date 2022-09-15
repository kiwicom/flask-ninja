Router
======

Working with Routers
````````````````````

Real world applications can almost never fit all logic into a single file.
As Flask supports splitting your API into smaller modules via Blueprints, in FlaskNinja the module is called Router.

When you create a new Router instance, you can register your endpoints there as to the Ninja API instance:

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


Then you combine all endpoints by adding the routers to the API. You can also add a prefix to endpoints of a router,
so you don't have to write the full path in each endpoint.

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


Now you can access the following endpoints:

* ``/blogs/``
* ``/blogs/new``
* ``/users/``
* ``/users/new``

**Note:** You can also add a router to a router, to create a more complex hierarchy of your api:

.. code-block:: python

    from flask_ninja import Router

    from .blogs import api as blogs_api
    from .users import api as users_api

    api = Router()

    api.add_router(blogs_api, prefix="/blogs")
    api.add_router(users_api, prefix="/users")

Auth
````

If you need a special authentication for all endpoints of a router, you can specify it when initializing the router:

.. code-block:: python

    api = Router(auth=BearerAuth())

This will overwrite the auth configuration of the API or routers above this router.
