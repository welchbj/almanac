"""Abstraction over an argument with immutable properties."""

from .argument_base import ArgumentBase
from ...errors import FrozenAccessError


class FrozenArgument(ArgumentBase):

    def _abstract_display_name_setter(
        self,
        new_display_name: str
    ) -> None:
        raise FrozenAccessError('Cannot change the display name of a FrozenCommand')
