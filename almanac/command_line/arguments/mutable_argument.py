"""Abstraction over an argument with mutable properties."""

from .argument_base import ArgumentBase
from .frozen_argument import FrozenArgument


class MutableArgument(ArgumentBase):

    def _abstract_display_name_setter(
        self,
        new_display_name: str
    ) -> None:
        self._display_name = new_display_name

    def freeze(
        self
    ) -> FrozenArgument:
        return FrozenArgument(
            self.param,
            name=self.display_name,
            description=self.description,
            completer=self.completer
        )
