"""An immutable command abstraction."""

from __future__ import annotations

from functools import cached_property
from typing import Any, Dict, Iterable, Iterator, Mapping, Optional, Tuple, Union

from .command_base import CommandBase
from ..arguments import FrozenArgument
from ..errors import FrozenAccessError, NoSuchArgumentError
from ..types import CommandCoroutine
from ..utils import abbreviated


class FrozenCommand(CommandBase, Mapping[str, FrozenArgument]):
    """A command abstraction that does not permit mutation of its fields."""

    def __init__(
        self,
        coroutine: CommandCoroutine,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[Union[str, Iterable[str]]] = None,
        argument_map: Optional[Mapping[str, FrozenArgument]] = None
    ) -> None:
        super().__init__(
            coroutine,
            name=name,
            description=description,
            aliases=aliases
        )

        self._argument_map: Mapping[str, FrozenArgument]
        if argument_map is None:
            self._argument_map = {}
        else:
            self._argument_map = {k: v for k, v in argument_map.items()}

    @cached_property
    def abbreviated_description(
        self
    ) -> str:
        """A shortened version of this command's description."""
        return abbreviated(self._description)

    def resolved_kwarg_names(
        self,
        kwarg_dict: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Transform keyword argument names from their display to real values.

        Argument display names are those that may have been overriden by the user. To
        transform a kwarg dict to a form suitable for binding to the original function
        definition, we must swap out these argument names to match the wrapped
        coroutine signature.

        Any keys in the :param:`kwarg_dict` argument that do not map to valid argument
        names will be present in the second dictionary returned.

        """
        resolved: Dict[str, Any] = {}
        unresolved: Dict[str, Any] = {}

        for display_name, value in kwarg_dict.items():
            if display_name in self.keys():
                real_name = self[display_name].real_name
                resolved[real_name] = value
            else:
                unresolved[display_name] = value

        return resolved, unresolved

    def _abstract_description_setter(
        self,
        new_description: str
    ) -> None:
        raise FrozenAccessError('Cannot change the description of a FrozenCommand')

    def _abstract_name_setter(
        self,
        new_name: str
    ) -> None:
        raise FrozenAccessError('Cannot change the name of a FrozenCommand')

    def add_alias(
        self,
        *aliases: str
    ) -> None:
        raise FrozenAccessError('Cannot add an alias to a FrozenCommand')

    def get_unbound_arguments(
        self,
        *args,
        **kwargs
    ) -> Tuple[FrozenArgument, ...]:
        """Compute a tuple of arguments that would be unbound with the given values.

        In the event of an error where the set of provided arguments cannot even be
        partially applied to the function signature, an empty tuple is returned.

        """
        try:
            bound_arguments = self._impl_signature.bind_partial(*args, **kwargs)
        except TypeError:
            return tuple()

        bound_param_names = set(bound_arguments.arguments.keys())
        unbound_arguments = tuple(
            self._argument_map[param_name]
            for param_name in self._impl_signature.parameters.keys()
            if param_name not in bound_param_names
        )

        return unbound_arguments

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

    def _hash_basis(
        self
    ) -> Tuple[Any, ...]:
        return (self.name, self.description, self.aliases, self.coroutine,)

    def __hash__(
        self
    ) -> int:
        return hash(self._hash_basis())

    def __eq__(
        self,
        other: Any
    ) -> bool:
        if not isinstance(other, FrozenCommand):
            return NotImplemented

        return self._hash_basis() == other._hash_basis()

    def __iter__(
        self
    ) -> Iterator[str]:
        return iter(self._argument_map)

    def __getitem__(
        self,
        argument_display_name: str
     ) -> FrozenArgument:
        try:
            return self._argument_map[argument_display_name]
        except KeyError:
            raise NoSuchArgumentError(argument_display_name)

    def __len__(
        self
    ) -> int:
        return len(self._argument_map.keys())
