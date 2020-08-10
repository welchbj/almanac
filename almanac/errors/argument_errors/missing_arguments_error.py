from __future__ import annotations

from typing import Tuple

from .base_argument_error import BaseArgumentError


class MissingArgumentsError(BaseArgumentError):
    """An exception type for missing arguments."""

    def __init__(
        self,
        *missing_args: str
    ) -> None:
        self._missing_args = missing_args

        if not missing_args:
            msg = 'Missing required argument(s).'
        elif len(missing_args) == 1:
            msg = f'Missing required argument {missing_args[0]}.'
        elif len(missing_args) == 2:
            msg = f'Missing required arguments {missing_args[0]} and {missing_args[1]}.'
        else:
            joined_names = ','.join(missing_args[:-1]) + f', and {missing_args[-1]}'
            msg = f'Missing required arguments {joined_names}.'

        super().__init__(msg)

    @property
    def missing_args(
        self
    ) -> Tuple[str, ...]:
        """The arguments that were missing."""
        return self._missing_args
