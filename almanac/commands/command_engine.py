"""Implementation of the ``CommandEngine`` class."""

from functools import lru_cache
from typing import List, MutableMapping, Tuple

from .command import Command
from ..errors import CommandNameCollisionError, NoSuchCommandError
from ..utils import FuzzyMatcher


class CommandEngine:
    """A command lookup engine."""

    def __init__(
        self,
        *commands_to_register: Command
    ) -> None:
        self._registered_commands: List[Command] = []
        self._command_lookup_table: MutableMapping[str, Command] = {}

        for command in commands_to_register:
            self.register(command)

    def register(
        self,
        command: Command
    ) -> None:
        """Register a command on this class.

        Raises:
            CommandNameCollisionError: If the ``name`` or one of the
                ``aliases`` on the specified :class:`Command` conflicts with an
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
    ) -> Command:
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

    @lru_cache(maxsize=256)
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

    @property
    def registered_commands(
        self
    ) -> List[Command]:
        """The :class:`Command`s registered on this instance."""
        return self._registered_commands

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
