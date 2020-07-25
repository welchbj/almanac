"""Abstraction over an argument with immutable properties."""

from prompt_toolkit.completion import Completer

from .argument_base import ArgumentBase
from ...errors import FrozenAccessError


class FrozenArgument(ArgumentBase):

    def _abstract_display_name_setter(
        self,
        new_display_name: str
    ) -> None:
        raise FrozenAccessError('Cannot change the display name of a FrozenCommand')

    def _abstract_completer_setter(
        self,
        new_completer: Completer
    ) -> None:
        raise FrozenAccessError('Cannot change the completer of a FrozenCommand')

    def _abstract_description_setter(
        self,
        new_description: str
    ) -> None:
        raise FrozenAccessError('Cannot change the description of a FrozenCommand')
