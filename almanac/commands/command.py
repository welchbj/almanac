"""Implementation of the ``Command`` class."""

from __future__ import annotations

import inspect
import itertools

from typing import Tuple

from .types import CommandCoroutine
from ..constants import CommandDefaults


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

    @property
    def signature(
        self
    ) -> inspect.Signature:
        """The signature of the user-written coroutine wrapped by this command."""
        return self._impl_signature

    async def run(
        self,
        *args,
        **kwargs
    ) -> int:
        """A thin wrapper around this command's user-provided coroutine.

        The return code follows the following pattern:
            0 -> No errors occured.
            Anything else -> Something went wrong.

        """
        return await self._impl_coroutine(*args, **kwargs)
