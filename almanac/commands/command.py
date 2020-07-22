"""Implementation of the ``Command`` class."""

from __future__ import annotations

import inspect
import itertools

import pyparsing as pp

from typing import Tuple

from .types import CommandCoroutine
from ..constants import CommandDefaults
from ..errors import CommandArgumentError
from ..utils import capitalized


class Command:
    """Encapsulation of a command."""

    def __init__(
        self,
        coroutine: CommandCoroutine
    ) -> None:
        # XXX: these fields will be able to come from decorators, too

        self._name = coroutine.__name__
        self._aliases: Tuple[str, ...] = tuple()

        maybe_doc = coroutine.__doc__
        self._doc = maybe_doc if maybe_doc is not None else CommandDefaults.DOC

        self._impl_signature = inspect.signature(coroutine)
        self._impl_coroutine = coroutine

    @property
    def name(
        self
    ) -> str:
        """The primary name of this function."""
        return self._name

    @property
    def doc(
        self
    ) -> str:
        """The documentation string for this command."""
        return self._doc

    @property
    def aliases(
        self
    ) -> Tuple[str, ...]:
        """Aliases for this command."""
        return self._aliases

    @property
    def identifiers(
        self
    ) -> Tuple[str, ...]:
        """A combination of this command's name and any of its aliases."""
        return tuple(itertools.chain(
            (self._name,),
            self._aliases
        ))

    async def run(
        self,
        args: pp.ParseResults
    ) -> int:
        """Run this command.

        The return code follows the following pattern:
            0 -> No errors occured.
            Anything else -> Something went wrong.

        """
        # Verify that we have a callable set of arguments.
        try:
            self._impl_signature.bind(*args.positionals, **args.kv)
        except TypeError as e:
            clean_err_msg = capitalized(str(e)) + '.'
            # TODO: this can also throw a type error if there are too many positionals
            bound_args = self._impl_signature.bind_partial(*args.positionals, **args.kv)
            raise CommandArgumentError(clean_err_msg, bound_args) from e

        # Verify the type of all arguments, and promote special cases.
        # TODO

        return await self._impl_coroutine(*args.positionals, **args.kv)
