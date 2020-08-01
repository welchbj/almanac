"""Implementation of an I/O context that goes no where."""

from typing import Any

from .abstract_io_context import AbstractIoContext


class NullIoContext(AbstractIoContext):
    """An input/output context for not actually printing anything."""

    def print_info(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        pass

    def print_warn(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        pass

    def print_err(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        pass

    def print_raw(
        self,
        *args,
        **kwargs
    ) -> None:
        pass
