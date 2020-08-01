"""almanac testing utilities."""

from almanac import Application, NullIoContext


class AlmanacTextMixin:

    def get_test_app(
        self
    ) -> Application:
        app = Application(
            io_ctx_cls=NullIoContext,
            propagate_runtime_exceptions=True
        )
        return app
