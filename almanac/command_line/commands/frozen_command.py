"""An immutable command abstraction."""

from __future__ import annotations
from almanac.errors.arguments.no_such_argument_error import NoSuchArgumentError

from typing import Any, Dict, Iterable, Iterator, Mapping, Optional, Tuple, Union

from .command_base import CommandBase
from ..arguments import FrozenArgument
from ..types import CommandCoroutine
from ...errors import FrozenAccessError


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

    # TODO: validate that all of the arguments of the wrapped coroutine are actually
    #       represented with an equivalent FrozenArgument?

    def resolved_kwarg_names(
        self,
        kwarg_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform keyword argument names from their display to real values.

        Argument display names are those that may have been overriden by the user. To
        transform a kwarg dict to a form suitable for binding to the original function
        defintion, we must swap out these argument names to match the wrapped coroutine
        signature.

        """
        return {
            self[name].real_name: value for name, value in kwarg_dict.items()
        }

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
            raise NoSuchArgumentError(
                f'No such argument with display name {argument_display_name}'
            )

    def __len__(
        self
    ) -> int:
        return len(self._argument_map.keys())
