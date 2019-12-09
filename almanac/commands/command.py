"""Implementation of the ``Command`` class."""

from __future__ import annotations

import itertools

from typing import (
    Iterable,
    Tuple,
    TYPE_CHECKING)

from .types import (
    CommandCallable,
    OptsType)

from ..io import (
    AbstractIoContext)

if TYPE_CHECKING:
    from ..application import (
        Application)


class Command:
    """Encapsulation of a command."""

    @staticmethod
    def from_callable(
        command_callable: CommandCallable
    ) -> Command:
        """Generate a :class:`Command` instance from a callable."""
        # TODO: this will not work with decorators
        return Command(
            name=command_callable.__name__,
            doc=command_callable.__doc__,  # type: ignore
            aliases=tuple(),
            impl_callable=command_callable
        )

    def __init__(
        self,
        name: str,
        doc: str,
        aliases: Iterable[str],
        impl_callable: CommandCallable
    ) -> None:
        self._name = name
        self._doc = doc
        self._aliases = tuple(aliases)
        self._impl_callable = impl_callable

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
        app: Application,
        io: AbstractIoContext,
        opts: OptsType
    ) -> int:
        """Run this command.

        The return code follows the following pattern:
            0 -> No errors occured.
            Anything else -> Something went wrong.

        """
        return await self._impl_callable(app, io, opts)
