"""Exception type for unknown issues in argument-binding."""

import inspect

from typing import Any, Dict, Iterable, Tuple

from .base_argument_error import BaseArgumentError


class UnknownArgumentBindingError(BaseArgumentError):
    """An exception type for unknown issues in argument-binding."""

    def __init__(
        self,
        signature: inspect.Signature,
        pos_args: Iterable[Any],
        kw_args: Dict[str, Any]
    ) -> None:
        super().__init__('Unknown argument-binding error.')
        self._signature = signature
        self._pos_args = tuple(pos_args)
        self._kw_args = kw_args

    @property
    def signature(
        self
    ) -> inspect.Signature:
        """The signature that could not be bound to."""
        return self._signature

    @property
    def pos_args(
        self
    ) -> Tuple[Any, ...]:
        """The pos_args that could not be bound to the signature."""
        return self._pos_args

    @property
    def kw_args(
        self
    ) -> Dict[str, Any]:
        """The kw_args that could not be bound to the signature."""
        return self._kw_args
