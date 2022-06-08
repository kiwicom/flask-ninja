import os


def get_path(rel: str) -> str:
    return os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), rel
    )


swagger_ui_4_12_0_path = get_path("swagger-ui-4.12.0")

swagger_ui_path = swagger_ui_4_12_0_path
