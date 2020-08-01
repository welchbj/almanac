"""Exception type for too many positional arguments being specified."""

from typing import Any, Tuple

from .base_argument_error import BaseArgumentError


class TooManyPositionalArgumentsError(BaseArgumentError):
    """An exception type for when too many positional arguments are specified."""

    def __init__(
        self,
        *values: Any
    ) -> None:
        if not values:
            raise ValueError('Must have at least one positional argument value')

        super().__init__(f'{len(values)} too many positional arguments.')
        self._values = values

    @property
    def values(
        self
    ) -> Tuple[Any, ...]:
        """A tuple of the excess positional argument values."""
        return self._values
