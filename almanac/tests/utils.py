"""almanac testing utilities."""

from almanac import Application, make_standard_app, NullIoContext


class AlmanacTextMixin:

    def get_test_app(
        self
    ) -> Application:
        app = make_standard_app(
            io_context_cls=NullIoContext,
            propagate_runtime_exceptions=True
        )
        return app