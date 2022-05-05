import pytest

from flask_ninja.operation import Callback, Operation
from flask_ninja.param import Param, ParamType
from flask_ninja.router import Router
from tests.conftest import BearerAuth


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


def some_view(foo_param: int) -> str:
    return str(foo_param)


@pytest.mark.parametrize(
    ("router", "another_router", "prefix", "result_operations"),
    [
        pytest.param(Router(), Router(), "/some_prefix", [], id="empty routers"),
        pytest.param(
            Router(),
            Router(operations=[Operation("/ping", "GET", some_view)]),
            "/some_prefix",
            [Operation("/some_prefix/ping", "GET", some_view)],
            id="empty_root_nonempty_add",
        ),
        pytest.param(
            Router(operations=[Operation("/ping", "GET", some_view)]),
            Router(),
            "/some_prefix",
            [Operation("/ping", "GET", some_view)],
            id="nonempty_root_empty_add",
        ),
        pytest.param(
            Router(operations=[Operation("/ping", "GET", some_view)]),
            Router(operations=[Operation("/ping", "GET", some_view)]),
            "/some_prefix",
            [
                Operation("/ping", "GET", some_view),
                Operation("/some_prefix/ping", "GET", some_view),
            ],
            id="not_set_auth_root_not_set_auth_add",
        ),
        pytest.param(
            Router(
                operations=[Operation("/ping", "GET", some_view, auth=None)], auth=None
            ),
            Router(operations=[Operation("/ping", "GET", some_view)]),
            "/some_prefix",
            [
                Operation("/ping", "GET", some_view, auth=None),
                Operation("/some_prefix/ping", "GET", some_view, auth=None),
            ],
            id="no_auth_root_not_set_auth_add",
        ),
        pytest.param(
            Router(
                operations=[Operation("/ping", "GET", some_view, auth=BearerAuth())],
                auth=BearerAuth(),
            ),
            Router(operations=[Operation("/ping", "GET", some_view)]),
            "/some_prefix",
            [
                Operation("/ping", "GET", some_view, auth=BearerAuth()),
                Operation("/some_prefix/ping", "GET", some_view, auth=BearerAuth()),
            ],
            id="bearer_auth_root_not_set_auth_add",
        ),
        pytest.param(
            Router(
                operations=[Operation("/ping", "GET", some_view, auth=BearerAuth())],
                auth=BearerAuth(),
            ),
            Router(
                operations=[Operation("/ping", "GET", some_view, auth=None)], auth=None
            ),
            "/some_prefix",
            [
                Operation("/ping", "GET", some_view, auth=BearerAuth()),
                Operation("/some_prefix/ping", "GET", some_view, auth=None),
            ],
            id="bearer_auth_root_no_auth_add",
        ),
    ],
)
def test_add_router(router, another_router, prefix, result_operations):
    router.add_router(another_router, prefix=prefix)

    assert len(router.operations) == len(result_operations)
    for operation, result_operation in zip(router.operations, result_operations):
        assert operation.path == result_operation.path
        assert operation.method == result_operation.method
        assert operation.auth == result_operation.auth
