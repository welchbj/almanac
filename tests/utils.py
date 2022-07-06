"""almanac testing utilities."""

from almanac import Application, make_standard_app, NullIoContext


def get_test_app(propagate_runtime_exceptions: bool = False) -> Application:
    app = make_standard_app(
        io_context_cls=NullIoContext,
        propagate_runtime_exceptions=propagate_runtime_exceptions,
    )
    return app
