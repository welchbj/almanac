"""Implementation of the ``CommandEngine`` class."""

import inspect

import pyparsing as pp

from typing import Any, Callable, Dict, List, MutableMapping, Tuple, Type

from ..commands import FrozenCommand
from ..errors import (
    CommandNameCollisionError,
    ConflictingPromoterTypesError,
    NoSuchArgumentError,
    NoSuchCommandError,
    UnknownArgumentBindingError
)
from ..types import is_matching_type
from ..utils import FuzzyMatcher


class CommandEngine:
    """A command lookup and management engine."""

    def __init__(
        self,
        *commands_to_register: FrozenCommand
    ) -> None:
        self._registered_commands: List[FrozenCommand] = []
        self._command_lookup_table: MutableMapping[str, FrozenCommand] = {}
        self._type_promoter_mapping: Dict[Type, Callable] = {}

        for command in commands_to_register:
            self.register(command)

    @property
    def type_promoter_mapping(
        self
    ) -> Dict[Type, Callable]:
        """A mapping of types to callables that convert raw arguments to those types."""
        return self._type_promoter_mapping

    def add_promoter_for_type(
        self,
        _type: Type,
        promoter_callable: Callable
    ) -> None:
        """Register a promotion callable for a specific argument type."""
        if _type in self._type_promoter_mapping.keys():
            raise ConflictingPromoterTypesError(
                f'Type {_type} already has a registered promoter callable '
                f'{promoter_callable}'
            )

        self._type_promoter_mapping[_type] = promoter_callable

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
        try:
            command: FrozenCommand = self[name_or_alias]
            coro_signature: inspect.Signature = command.signature
        except NoSuchCommandError as e:
            raise e

        args = [x for x in parsed_args.positionals]
        raw_kwargs = {k: v for k, v in parsed_args.kv.asDict().items()}
        resolved_kwargs, unresolved_kwargs = command.resolved_kwarg_names(raw_kwargs)
        merged_kwarg_dicts = {**resolved_kwargs, **unresolved_kwargs}

        try:
            bound_args = command.signature.bind(*args, **merged_kwarg_dicts)
            can_bind = True
        except TypeError:
            can_bind = False

        # If we can call our function, we next promote all promotable arguments and
        # execute the call.
        if can_bind:
            for arg_name, value in bound_args.arguments.items():
                param = coro_signature.parameters[arg_name]
                arg_annotation = param.annotation

                for _type, promoter_callable in self._type_promoter_mapping.items():
                    if not is_matching_type(_type, arg_annotation):
                        continue

                    new_value: Any
                    if param.kind == param.VAR_POSITIONAL:
                        # Promote over all entries in a *args variant.
                        new_value = tuple(promoter_callable(x) for x in value)
                    elif param.kind == param.VAR_KEYWORD:
                        # Promote over all values in a **kwargs variant.
                        new_value = {
                            k: promoter_callable(v) for k, v in value.items()
                        }
                    else:
                        # Promote a single value.
                        new_value = promoter_callable(value)

                    bound_args.arguments[arg_name] = new_value

            return await command.run(*bound_args.args, **bound_args.kwargs)

        # Otherwise, we do some inspection to generate an informative error.
        try:
            partially_bound_args = command.signature.bind_partial(
                *args, **merged_kwarg_dicts
            )
            partially_bound_args.apply_defaults()
            can_partially_bind = True
        except TypeError:
            can_partially_bind = False

        if not can_partially_bind:
            # Check if the failure is due to an invalid kwarg name.
            if not command.has_var_kw_arg:
                possible_kwargs = set(command.keys())
                extra_kwargs = [
                    x for x in merged_kwarg_dicts if x not in possible_kwargs
                ]

                if extra_kwargs:
                    raise NoSuchArgumentError(*extra_kwargs)

            # Otherwise, it's possible that too many positional arguments were provided.
            if not command.has_var_pos_arg:
                pass

            # Something else went wrong.
            raise UnknownArgumentBindingError('Unknown argument binding error')

        # If we got this far, then we could at least partially bind to the coroutine
        # signature. This means we are likely just missing some required arguments,
        # which we can now enumerate.
        # TODO

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
