from typing import List

from prompt_toolkit.completion import Completer

from almanac.arguments.argument_base import ArgumentBase
from almanac.arguments.frozen_argument import FrozenArgument


class MutableArgument(ArgumentBase):
    """An encapsulation of an argument which can be mutated."""

    def _abstract_display_name_setter(self, new_display_name: str) -> None:
        self._display_name = new_display_name

    def _abstract_description_setter(self, new_description: str) -> None:
        self._description = new_description

    def _abstract_hidden_setter(self, new_value: bool) -> None:
        self._hidden = new_value

    @property
    def completers(self) -> List[Completer]:
        return self._completers

    def freeze(self) -> FrozenArgument:
        return FrozenArgument(
            self.param,
            name=self.display_name,
            description=self.description,
            completers=self.completers,
            hidden=self.hidden,
        )
