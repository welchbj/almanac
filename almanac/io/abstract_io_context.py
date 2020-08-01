"""Implementation of the ``AbstractIoContext`` class."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractIoContext(ABC):
    """An interface for input/output contexts."""

    @abstractmethod
    def print_info(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Print an information message."""

    @abstractmethod
    def print_warn(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Print a warning message."""

    @abstractmethod
    def print_err(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Print an error message."""

    @abstractmethod
    def print_raw(
        self,
        *args,
        **kwargs
    ) -> None:
        """Print raw, un-formatted text."""

    # TODO: need read/write-esque stuff if supporting files
    #       all print_* style commands could just be variations on write
