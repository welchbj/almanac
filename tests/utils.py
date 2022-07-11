"""almanac testing utilities."""

from almanac import (
    Application,
    NullIoContext,
    StandardConsoleIoContext,
    make_standard_app,
)


def get_test_app(
    null_output: bool = True, propagate_runtime_exceptions: bool = False
) -> Application:
    if null_output:
        io_ctx_cls = NullIoContext
    else:
        io_ctx_cls = StandardConsoleIoContext

    app = make_standard_app(
        io_context_cls=io_ctx_cls,
        propagate_runtime_exceptions=propagate_runtime_exceptions,
    )
    return app
