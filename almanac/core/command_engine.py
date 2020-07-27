"""Implementation of the ``CommandEngine`` class."""

import pyparsing as pp

from typing import List, MutableMapping, Tuple

from ..commands import FrozenCommand
from ..errors import CommandNameCollisionError, NoSuchCommandError
from ..utils import FuzzyMatcher


class CommandEngine:
    """A command lookup and management engine."""

    def __init__(
        self,
        *commands_to_register: FrozenCommand
    ) -> None:
        self._registered_commands: List[FrozenCommand] = []
        self._command_lookup_table: MutableMapping[str, FrozenCommand] = {}

        for command in commands_to_register:
            self.register(command)

    def register(
        self,
        command: FrozenCommand
    ) -> None:
        """Register a command on this class.

        Raises:
            CommandNameCollisionError: If the ``name`` or one of the
                ``aliases`` on the specified :class:`FrozenCommand` conflicts with an
                entry already stored in this :class:`CommandEngine`.

        """
        already_mapped = tuple(
            identifier for identifier in command.identifiers
            if identifier in self._command_lookup_table.keys()
        )
        if already_mapped:
            mapped_names = ', '.join(already_mapped)
            raise CommandNameCollisionError(
                'Identifier(s) ' + mapped_names + ' already mapped'
            )

        for identifier in command.identifiers:
            self._command_lookup_table[identifier] = command
        self._registered_commands.append(command)

    def get(
        self,
        name_or_alias: str
    ) -> FrozenCommand:
        """Get a :class:`Command` by its name or alias.

        Returns:
            The mapped :class:`Command` instance.

        Raises:
            NoSuchCommandError: If the specified ``name_or_alias`` is not contained
                within this instance.

        """
        if name_or_alias not in self._command_lookup_table.keys():
            raise NoSuchCommandError(
                '`' + name_or_alias + '` is not a configured command name or alias'
            )

        return self._command_lookup_table[name_or_alias]

    __getitem__ = get

    async def run(
        self,
        name_or_alias: str,
        parsed_args: pp.ParseResults
    ) -> int:
        """Run a command, validating the specified arguments."""
        args = parsed_args.positionals
        kwargs = parsed_args.kv

        # TODO: we need to update kwargs to reflect the names of the actual coro args

        try:
            command: FrozenCommand = self[name_or_alias]
        except NoSuchCommandError as e:
            raise e

        try:
            bound_args = command.signature.bind(*args, **kwargs)
            can_bind = True
        except TypeError:
            can_bind = False

        # TODO: Attempt to promote arguments to their desired type, if the argument is
        # not of the expected type and promotion callback exists.

        # If we can call our function, we do so.
        if can_bind:
            return await command.run(*args, **kwargs)

        # Otherwise, we need to figure out what went wrong.
        # TODO
        raise NotImplementedError('Need to implement error generation here')

    def get_suggestions(
        self,
        name_or_alias: str,
        max_suggestions: int = 3
    ) -> Tuple[str, ...]:
        """Find the closest matching names/aliases to the specified string.

        Returns:
            A possibly-empty tuple of :class:`Command`s that most
            closely match the specified `name_or_alias` field.

        """
        fuzz = FuzzyMatcher(
            name_or_alias,
            self._command_lookup_table.keys(),
            num_max_matches=max_suggestions
        )
        return fuzz.matches

    def keys(
        self
    ) -> Tuple[str, ...]:
        """Get a tuple of all registered command names and aliases."""
        return tuple(self._command_lookup_table.keys())

    @property
    def registered_commands(
        self
    ) -> Tuple[FrozenCommand, ...]:
        """The :class:`FrozenCommand`s registered on this instance."""
        return tuple(self._registered_commands)

    def __contains__(
        self,
        name_or_alias: str
    ) -> bool:
        """Whether a specified command name or alias is mapped."""
        return name_or_alias in self._command_lookup_table.keys()

    def __len__(
        self
    ) -> int:
        """The number of total names/aliases mapped in this instance."""
        return len(self._command_lookup_table.keys())

    def __repr__(
        self
    ) -> str:
        return f'<{self.__class__.__qualname__} [{str(self)}]>'

    def __str__(
        self
    ) -> str:
        return (
            f'{len(self)} names mapped to {len(self._registered_commands)} commands'
        )
