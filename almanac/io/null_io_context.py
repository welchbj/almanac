from typing import Any

from .abstract_io_context import AbstractIoContext


class NullIoContext(AbstractIoContext):
    """An input/output context for not actually printing anything."""

    def info(self, *args: Any, **kwargs: Any) -> None:
        pass

    def warn(self, *args: Any, **kwargs: Any) -> None:
        pass

    def error(self, *args: Any, **kwargs: Any) -> None:
        pass

    def raw(self, *args, **kwargs) -> None:
        pass

    def ansi(self, *args, **kwargs) -> None:
        pass
