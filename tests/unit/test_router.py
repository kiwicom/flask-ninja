from flask_ninja.operation import Callback
from flask_ninja.param import Param, ParamType
from flask_ninja.router import Router


def test_add_route_all_params():
    router = Router()
    callback = Callback(
        name="some_name",
        url="some_url",
        method="some_callback_method",
        response_codes={},
    )

    param = Param("some_param", int, ParamType.QUERY)

    @router.add_route(
        "GET",
        "/foo",
        responses={200: str},
        auth="some_auth",
        summary="some_summary",
        description="some_description",
        params={"foo_param": param},
        callbacks=[callback],
    )
    def sample_method():
        return "foo"

    assert len(router.operations) == 1
    assert router.operations[0].path == "/foo"
    assert router.operations[0].method == "GET"
    assert router.operations[0].responses == {200: str}
    assert router.operations[0].callbacks == [callback]
    assert router.operations[0].summary == "some_summary"
    assert router.operations[0].description == "some_description"
    assert router.operations[0].params == {"foo_param": param}


def test_add_route_no_params():
    router = Router()

    @router.add_route(
        "GET",
        "/foo",
    )
    def sample_method() -> str:
        return "foo"

    assert len(router.operations) == 1
    assert router.operations[0].path == "/foo"
    assert router.operations[0].method == "GET"
    assert router.operations[0].responses == {200: str}
    assert router.operations[0].callbacks is None
    assert router.operations[0].summary == ""
    assert router.operations[0].description == ""
    assert router.operations[0].params == {}
