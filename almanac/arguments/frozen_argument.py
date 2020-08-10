from functools import cached_property
from typing import Tuple

from prompt_toolkit.completion import Completer

from .argument_base import ArgumentBase
from ..errors import FrozenAccessError
from ..utils import abbreviated


class FrozenArgument(ArgumentBase):

    def _abstract_display_name_setter(
        self,
        new_display_name: str
    ) -> None:
        raise FrozenAccessError('Cannot change the display name of a FrozenArgument')

    def _abstract_description_setter(
        self,
        new_description: str
    ) -> None:
        raise FrozenAccessError('Cannot change the description of a FrozenArgument')

    def _abstract_hidden_setter(
        self,
        new_value: bool
    ) -> None:
        raise FrozenAccessError('Cannot change the hidden status of a FrozenArgument')

    @cached_property
    def abbreviated_description(
        self
    ) -> str:
        """A shortened version of this arguments description."""
        return abbreviated(self._description)

    @property
    def completers(
        self
    ) -> Tuple[Completer, ...]:
        return tuple(self._completers)
