"""Implementation of the ``StandardConsoleIoContext`` class."""

from typing import Any

from prompt_toolkit import HTML, print_formatted_text

from .abstract_io_context import AbstractIoContext


class StandardConsoleIoContext(AbstractIoContext):
    """An input/output context for printing information to the console."""

    def print_info(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansicyan>[*]</ansicyan>'), *args, **kwargs)

    def print_warn(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansiyellow>[!]</ansiyellow>'), *args, **kwargs)

    def print_err(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansired>[!]</ansired>'), *args, **kwargs)

    def print_raw(
        self,
        *args,
        **kwargs
    ) -> None:
        print_formatted_text(*args, **kwargs)
