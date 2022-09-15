API configuration
=================
Flask Ninja provides several helpful tools to deal with the most common API scenarios.
In order to setup Flask Ninja, you create your Flask instance and then using it, initialize NinjaAPI.

.. code-block:: python

    from flask import Flask
    from flask_ninja import NinjaAPI
    from pydantic import BaseModel

    app = Flask(__name__)
    api = NinjaAPI(app)

Then adding endpoints is as easy as adding them to normal flask api, you just add them not via the flask instance, but via the flask-ninja instance.

.. code-block:: python

    @api.get("/compute")
    def compute(a: int, b: int) -> Response:

**Note:** You can also add the endpoints via the flask instance and it will work, however then you loose all the flask-ninja benefits.


Configuration
-------------

NinjaAPI allows to be configured via the following arguments:

* **auth** - setup authentication for all endpoints in the API - this can be overriden by setting up different (or no) authentication method in a router or an endpoint.
* **title** - title of your application that is displayed in the swagger documentation
* **description** - description of your application that is displayed in the swagger documentation
* **version** - version of your application displayed in the swagger documentation
* **servers** - list of available servers running the application - setup for swagger
* **prefix** - add prefix to all endpoints
* **docs_url** - url for the swagger documentation - default ``/docs``
