from __future__ import annotations

import inspect

from typing import Any, Dict, Iterable, Tuple

from .almanac_error import AlmanacError
from .generic_errors import AlmanacKeyError


class BaseArgumentError(AlmanacError):
    """The base exception type for invalid arguments."""


class ArgumentNameCollisionError(BaseArgumentError):
    """An exception type for when argument names would collide."""

    def __init__(self, *names: str) -> None:
        if not names:
            msg = "Cannot map multiple arguments with the same identifier."
        elif len(names) == 1:
            msg = f"Cannot map multiple arguments with the same identifer {names[0]}."
        elif len(names) == 2:
            msg = (
                "Cannot map multiple arguments with the same identifiers "
                f"{names[0]} and {names[1]}."
            )
        else:
            joined_names = ",".join(names[:-1]) + f", and {names[-1]}"
            msg = f"Cannot map multiple arguments the same identifiers {joined_names}."

        super().__init__(msg)
        self._names = names

    @property
    def names(self) -> Tuple[str, ...]:
        """A tuple of the argument names that spawned this error."""
        return self._names


class InvalidArgumentNameError(BaseArgumentError):
    """An exception type for attempting to register invalid argument names."""


class MissingArgumentsError(BaseArgumentError):
    """An exception type for missing arguments."""

    def __init__(self, *missing_args: str) -> None:
        self._missing_args = missing_args

        if not missing_args:
            msg = "Missing required argument(s)."
        elif len(missing_args) == 1:
            msg = f"Missing required argument {missing_args[0]}."
        elif len(missing_args) == 2:
            msg = f"Missing required arguments {missing_args[0]} and {missing_args[1]}."
        else:
            joined_names = ",".join(missing_args[:-1]) + f", and {missing_args[-1]}"
            msg = f"Missing required arguments {joined_names}."

        super().__init__(msg)

    @property
    def missing_args(self) -> Tuple[str, ...]:
        """The arguments that were missing."""
        return self._missing_args


class NoSuchArgumentError(BaseArgumentError, AlmanacKeyError):
    """An exception type for resolutions of non-existent arguments."""

    def __init__(self, *names: str) -> None:
        if not names:
            msg = "No such argument with specified name."
        elif len(names) == 1:
            msg = f"No such argument with name {names[0]}."
        elif len(names) == 2:
            msg = f"No arguments exist with the name {names[0]} or {names[1]}."
        else:
            joined_names = ",".join(names[:-1]) + f", or {names[-1]}"
            msg = f"No arguments exist with the name {joined_names}."

        super().__init__(msg)
        self._names = names

    @property
    def names(self) -> Tuple[str, ...]:
        """A tuple of the argument names that triggered this error."""
        return self._names


class TooManyPositionalArgumentsError(BaseArgumentError):
    """An exception type for when too many positional arguments are specified."""

    def __init__(self, *values: Any) -> None:
        if not values:
            raise ValueError("Must have at least one positional argument value")

        super().__init__(f"{len(values)} too many positional arguments.")
        self._values = values

    @property
    def values(self) -> Tuple[Any, ...]:
        """A tuple of the excess positional argument values."""
        return self._values


class UnknownArgumentBindingError(BaseArgumentError):
    """An exception type for unknown issues in argument-binding."""

    def __init__(
        self,
        signature: inspect.Signature,
        pos_args: Iterable[Any],
        kw_args: Dict[str, Any],
    ) -> None:
        super().__init__("Unknown argument-binding error.")
        self._signature = signature
        self._pos_args = tuple(pos_args)
        self._kw_args = kw_args

    @property
    def signature(self) -> inspect.Signature:
        """The signature that could not be bound to."""
        return self._signature

    @property
    def pos_args(self) -> Tuple[Any, ...]:
        """The pos_args that could not be bound to the signature."""
        return self._pos_args

    @property
    def kw_args(self) -> Dict[str, Any]:
        """The kw_args that could not be bound to the signature."""
        return self._kw_args
