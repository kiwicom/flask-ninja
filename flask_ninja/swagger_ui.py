import os


def get_path(rel: str) -> str:
    return os.path.join(
        os.path.abspath(os.path.dirname(os.path.realpath(__file__))), rel
    )


swagger_ui_5_9_1_path = get_path("swagger-ui-5.9.1")

swagger_ui_path = swagger_ui_5_9_1_path
