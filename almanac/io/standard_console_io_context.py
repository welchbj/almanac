from typing import Any

from prompt_toolkit import ANSI, HTML, print_formatted_text

from .abstract_io_context import AbstractIoContext


class StandardConsoleIoContext(AbstractIoContext):
    """An input/output context for printing information to the console."""

    def info(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansicyan>[*]</ansicyan>'), *args, **kwargs)

    def warn(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansiyellow>[!]</ansiyellow>'), *args, **kwargs)

    def error(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        print_formatted_text(HTML('<ansired>[!]</ansired>'), *args, **kwargs)

    def raw(
        self,
        *args,
        **kwargs
    ) -> None:
        print_formatted_text(*args, **kwargs)

    def ansi(
        self,
        *args,
        **kwargs
    ) -> None:
        ansi_args = iter(ANSI(arg) for arg in args)
        print_formatted_text(*ansi_args, **kwargs)
