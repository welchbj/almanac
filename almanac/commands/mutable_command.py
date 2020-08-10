from __future__ import annotations

import asyncio

from collections import Counter
from typing import Iterable, Iterator, Mapping, MutableMapping, Optional, Union

from .command_base import CommandBase
from .frozen_command import FrozenCommand
from ..arguments import MutableArgument
from ..errors import (
    ArgumentNameCollisionError,
    CommandRegistrationError,
    NoSuchArgumentError
)
from ..types import CommandCoroutine


class MutableCommand(CommandBase, MutableMapping[str, MutableArgument]):
    """A command abstraction that allows for modification of its fields.

    The arguments of this command can be accessed via dict-like operations on instances
    of this class. Of note is that the keys for this dictionary are the argument names
    of the internal coroutine from this function (in contrast to a
    :class:`FrozenCommand`, which is keyed based on a :class:`ArgumentBase`'s
    ``display_name`` property).

    """

    def __init__(
        self,
        coroutine: CommandCoroutine,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[Union[str, Iterable[str]]] = None,
        argument_map: Optional[Mapping[str, MutableArgument]] = None
    ) -> None:
        super().__init__(
            coroutine,
            name=name,
            description=description,
            aliases=aliases
        )

        self._argument_map: MutableMapping[str, MutableArgument] = {}
        for param_name, param in self._impl_signature.parameters.items():
            self._argument_map[param_name] = MutableArgument(param)

        if argument_map is not None:
            self._argument_map.update(argument_map)

    __hash__ = None  # type: ignore

    @staticmethod
    def ensure_command(
        new_command: Union[MutableCommand, CommandCoroutine]
    ) -> MutableCommand:
        if not isinstance(new_command, MutableCommand):
            if not asyncio.iscoroutinefunction(new_command):
                raise CommandRegistrationError(
                    'Attempted to create a command with something other than an async '
                    f'function or MutableCommand: {new_command.__class__.__qualname__}'
                )

            new_command = MutableCommand(new_command)

        return new_command

    def _abstract_description_setter(
        self,
        new_description: str
    ) -> None:
        self._description = new_description

    def _abstract_name_setter(
        self,
        new_name: str
    ) -> None:
        self._name = new_name

    def add_alias(
        self,
        *aliases: str
    ) -> None:
        for alias in aliases:
            self._aliases.append(alias)

    def freeze(
        self
    ) -> FrozenCommand:
        """Convert this instance into a :class:`FrozenCommand`."""
        display_name_counter = Counter(arg.display_name for arg in self.values())

        conflicting_arg_names = [
            display_name for display_name, count in display_name_counter.items()
            if count > 1
        ]
        if conflicting_arg_names:
            raise ArgumentNameCollisionError(*conflicting_arg_names)

        frozen_argument_map = {
            arg.display_name: arg.freeze() for arg in self.values()
        }

        return FrozenCommand(
            self.coroutine,
            name=self.name,
            description=self.description,
            aliases=self.aliases,
            argument_map=frozen_argument_map
        )

    def __delitem__(
        self,
        argument_real_name: str
    ) -> None:
        try:
            del self._argument_map[argument_real_name]
        except KeyError:
            raise NoSuchArgumentError(argument_real_name)

    def __iter__(
        self
    ) -> Iterator[str]:
        return iter(self._argument_map)

    def __getitem__(
        self,
        argument_real_name: str
     ) -> MutableArgument:
        try:
            return self._argument_map[argument_real_name]
        except KeyError:
            raise NoSuchArgumentError(argument_real_name)

    def __len__(
        self
    ) -> int:
        return len(self._argument_map.keys())

    def __setitem__(
        self,
        argument_real_name: str,
        argument: MutableArgument
    ) -> None:
        self._argument_map[argument_real_name] = argument
