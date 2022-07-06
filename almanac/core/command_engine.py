from __future__ import annotations

import inspect

import pyparsing as pp

from typing import (
    Any,
    Callable,
    Dict,
    List,
    MutableMapping,
    Tuple,
    Type,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

from ..commands import FrozenCommand
from ..errors import (
    CommandNameCollisionError,
    ConflictingPromoterTypesError,
    MissingArgumentsError,
    NoSuchArgumentError,
    NoSuchCommandError,
    TooManyPositionalArgumentsError,
    UnknownArgumentBindingError,
)
from ..hooks import AsyncHookCallback, PromoterFunction
from ..types import is_matching_type
from ..utils import FuzzyMatcher

if TYPE_CHECKING:
    from .application import Application

HookCallbackMapping = MutableMapping[FrozenCommand, List[AsyncHookCallback]]

_T = TypeVar("_T")


class CommandEngine:
    """A command lookup and management engine."""

    def __init__(self, app: Application, *commands_to_register: FrozenCommand) -> None:
        self._app = app

        self._registered_commands: List[FrozenCommand] = []
        self._command_lookup_table: Dict[str, FrozenCommand] = {}

        self._after_command_callbacks: HookCallbackMapping = {}
        self._before_command_callbacks: HookCallbackMapping = {}

        for command in commands_to_register:
            self.register(command)

        self._type_promoter_mapping: Dict[Type, Callable] = {}

    @property
    def app(self) -> Application:
        """The application that this engine manages."""
        return self._app

    @property
    def type_promoter_mapping(self) -> Dict[Type, Callable]:
        """A mapping of types to callables that convert raw arguments to those types."""
        return self._type_promoter_mapping

    def add_promoter_for_type(
        self, _type: Type[_T], promoter_callable: PromoterFunction[_T]
    ) -> None:
        """Register a promotion callable for a specific argument type."""
        if _type in self._type_promoter_mapping.keys():
            raise ConflictingPromoterTypesError(
                f"Type {_type} already has a registered promoter callable "
                f"{promoter_callable}"
            )

        self._type_promoter_mapping[_type] = promoter_callable

    def register(self, command: FrozenCommand) -> None:
        """Register a command on this class.

        Raises:
            CommandNameCollisionError: If the ``name`` or one of the
                ``aliases`` on the specified :class:`FrozenCommand` conflicts with an
                entry already stored in this :class:`CommandEngine`.

        """
        already_mapped_names = tuple(
            identifier
            for identifier in command.identifiers
            if identifier in self._command_lookup_table.keys()
        )
        if already_mapped_names:
            raise CommandNameCollisionError(*already_mapped_names)

        for identifier in command.identifiers:
            self._command_lookup_table[identifier] = command

        self._after_command_callbacks[command] = []
        self._before_command_callbacks[command] = []

        self._registered_commands.append(command)

    def add_before_command_callback(
        self, name_or_command: Union[str, FrozenCommand], callback: AsyncHookCallback
    ) -> None:
        """Register a callback for execution before a command."""
        if isinstance(name_or_command, str):
            try:
                command = self[name_or_command]
            except KeyError:
                raise NoSuchCommandError(name_or_command)
        else:
            command = name_or_command

        self._before_command_callbacks[command].append(callback)

    def add_after_command_callback(
        self, name_or_command: Union[str, FrozenCommand], callback: AsyncHookCallback
    ) -> None:
        """Register a callback for execution after a command."""
        if isinstance(name_or_command, str):
            try:
                command = self[name_or_command]
            except KeyError:
                raise NoSuchCommandError(name_or_command)
        else:
            command = name_or_command

        self._after_command_callbacks[command].append(callback)

    def get(self, name_or_alias: str) -> FrozenCommand:
        """Get a :class:`FrozenCommand` by its name or alias.

        Returns:
            The mapped :class:`FrozenCommand` instance.

        Raises:
            :class:`NoSuchCommandError`: If the specified ``name_or_alias`` is not
                contained within this instance.

        """
        if name_or_alias not in self._command_lookup_table.keys():
            raise NoSuchCommandError(name_or_alias)

        return self._command_lookup_table[name_or_alias]

    __getitem__ = get

    async def run(self, name_or_alias: str, parsed_args: pp.ParseResults) -> int:
        """Run a command, validating the specified arguments.

        In the event of coroutine-binding failure, this method will do quite a bit of
        signature introspection to determine why a binding of user-specified arguments
        to the coroutine signature might fail.

        """
        try:
            command: FrozenCommand = self[name_or_alias]
            coro_signature: inspect.Signature = command.signature
        except NoSuchCommandError as e:
            raise e

        pos_arg_values = [x for x in parsed_args.positionals]
        raw_kwargs = {k: v for k, v in parsed_args.kv.asDict().items()}
        resolved_kwargs, unresolved_kwargs = command.resolved_kwarg_names(raw_kwargs)

        # Check if we have any extra/unresolvable kwargs.
        if not command.has_var_kw_arg and unresolved_kwargs:
            extra_kwargs = list(unresolved_kwargs.keys())
            raise NoSuchArgumentError(*extra_kwargs)

        # We can safely merged these kwarg dicts now since we know any unresolvable
        # arguments must be due to a **kwargs variant.
        merged_kwarg_dicts = {**unresolved_kwargs, **resolved_kwargs}

        try:
            bound_args = command.signature.bind(*pos_arg_values, **merged_kwarg_dicts)
            can_bind = True
        except TypeError:
            can_bind = False

        # If we can call our function, we next promote all eligible arguments and
        # execute the coroutine call.
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
                        new_value = {k: promoter_callable(v) for k, v in value.items()}
                    else:
                        # Promote a single value.
                        new_value = promoter_callable(value)

                    bound_args.arguments[arg_name] = new_value

            await self._app.run_async_callbacks(
                self._before_command_callbacks[command],
                *bound_args.args,
                **bound_args.kwargs,
            )
            ret = await command.run(*bound_args.args, **bound_args.kwargs)
            await self._app.run_async_callbacks(
                self._after_command_callbacks[command],
                *bound_args.args,
                **bound_args.kwargs,
            )
            return ret

        # Otherwise, we do some inspection to generate an informative error.
        try:
            partially_bound_args = command.signature.bind_partial(
                *pos_arg_values, **merged_kwarg_dicts
            )
            partially_bound_args.apply_defaults()
            can_partially_bind = True
        except TypeError:
            can_partially_bind = False

        if not can_partially_bind:
            # Check if too many positional arguments were provided.
            if not command.has_var_pos_arg:
                pos_arg_types = (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                unbound_pos_args = [
                    param
                    for name, param in command.signature.parameters.items()
                    if param.kind in pos_arg_types and name not in merged_kwarg_dicts
                ]

                if len(pos_arg_values) > len(unbound_pos_args):
                    unbound_values = pos_arg_values[len(unbound_pos_args) :]
                    raise TooManyPositionalArgumentsError(*unbound_values)

            # Something else went wrong.
            # XXX: should we be collecting more information here?
            raise UnknownArgumentBindingError(
                command.signature, pos_arg_values, merged_kwarg_dicts
            )

        # If we got this far, then we could at least partially bind to the coroutine
        # signature. This means we are likely just missing some required arguments,
        # which we can now enumerate.
        missing_arguments = (
            x
            for x in command.signature.parameters
            if x not in partially_bound_args.arguments.keys()
        )
        if not missing_arguments:
            raise UnknownArgumentBindingError(
                command.signature, pos_arg_values, merged_kwarg_dicts
            )

        raise MissingArgumentsError(*missing_arguments)

    def get_suggestions(
        self, name_or_alias: str, max_suggestions: int = 3
    ) -> Tuple[str, ...]:
        """Find the closest matching names/aliases to the specified string.

        Returns:
            A possibly-empty tuple of :class:`Command`s that most
            closely match the specified `name_or_alias` field.

        """
        fuzz = FuzzyMatcher(
            name_or_alias,
            self._command_lookup_table.keys(),
            num_max_matches=max_suggestions,
        )
        return fuzz.matches

    def keys(self) -> Tuple[str, ...]:
        """Get a tuple of all registered command names and aliases."""
        return tuple(self._command_lookup_table.keys())

    @property
    def registered_commands(self) -> Tuple[FrozenCommand, ...]:
        """The :py:class:`FrozenCommand` instances registered on this engine."""
        return tuple(self._registered_commands)

    def __contains__(self, name_or_alias: str) -> bool:
        """Whether a specified command name or alias is mapped."""
        return name_or_alias in self._command_lookup_table.keys()

    def __len__(self) -> int:
        """The number of total names/aliases mapped in this instance."""
        return len(self._command_lookup_table.keys())

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} [{str(self)}]>"

    def __str__(self) -> str:
        return f"{len(self)} names mapped to {len(self._registered_commands)} commands"
