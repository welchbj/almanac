"""Exception type for missing arguments."""

from __future__ import annotations

from typing import Iterable, Tuple

from .base_argument_error import BaseArgumentError


class MissingArgumentsError(BaseArgumentError):
    """An exception type for missing arguments."""

    def __init__(
        self,
        *missing_args: Iterable[str]
    ) -> None:
        self._missing_args = tuple(missing_args)

    @property
    def missing_args(
        self
    ) -> Tuple[str, ...]:
        """The arguments that were missing."""
        return self._missing_args
