"""A class for encapsulating command arguments."""

from abc import ABC, abstractmethod, abstractproperty
from inspect import Parameter
from typing import Any, Iterable, Optional, Union

from prompt_toolkit.completion import Completer

from ..constants import CommandLineDefaults


class ArgumentBase(ABC):
    """A class for encapsulating a command argument."""

    def __init__(
        self,
        param: Parameter,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        completers: Optional[Union[Completer, Iterable[Completer]]] = None,
        hidden: bool = False
    ) -> None:
        self._param = param

        self._real_name = param.name
        self._display_name = name if name is not None else self._real_name

        self._description = (
            description if description is not None else CommandLineDefaults.DOC
        )

        if completers is None:
            self._completers = []
        elif isinstance(completers, Completer):
            self._completers = [completers]
        else:
            # Assume we have iterable of completers.
            self._completers = [x for x in completers]

        self._hidden = hidden

    @property
    def display_name(
        self
    ) -> str:
        """The name used to specify this argument from the interactive shell."""
        return self._display_name

    @display_name.setter
    def display_name(
        self,
        new_display_name: str
    ) -> None:
        self._abstract_display_name_setter(new_display_name)

    @abstractmethod
    def _abstract_display_name_setter(
        self,
        new_display_name: str
    ) -> None:
        """Abstract display name setter to allow for access control."""

    @abstractproperty
    def completers(
        self
    ) -> Iterable[Completer]:
        """The registered completers for this argument."""

    @property
    def description(
        self
    ) -> str:
        """A description of what this argument does."""
        return self._description

    @description.setter
    def description(
        self,
        new_description: str
    ) -> None:
        self._abstract_description_setter(new_description)

    @abstractmethod
    def _abstract_description_setter(
        self,
        new_description: str
    ) -> None:
        """Abstract description setter to allow for access control."""

    @property
    def hidden(
        self
    ) -> bool:
        """Whether this argument should be hidden in the interactive prompt."""
        return self._hidden

    @hidden.setter
    def hidden(
        self,
        new_value: bool
    ) -> None:
        self._abstract_hidden_setter(new_value)

    @abstractmethod
    def _abstract_hidden_setter(
        self,
        new_value: bool
    ) -> None:
        """Abstract hidden setter to allow for access control."""

    @property
    def real_name(
        self
    ) -> str:
        """The name of this argument within the actual command coroutine."""
        return self._real_name

    @property
    def param(
        self
    ) -> Parameter:
        """The internal :class:`inspect.Parameter` wrapped by this class."""
        return self._param

    @property
    def annotation(
        self
    ) -> Any:
        """The annotated type of this parameter."""
        return self._param.annotation

    @property
    def is_pos_only(
        self
    ) -> bool:
        return self._param.kind == self._param.POSITIONAL_ONLY

    @property
    def is_kw_only(
        self
    ) -> bool:
        return self._param.kind == self._param.KEYWORD_ONLY

    @property
    def is_var_kw(
        self
    ) -> bool:
        return self._param.kind == self._param.VAR_KEYWORD

    @property
    def is_var_pos(
        self
    ) -> bool:
        return self._param.kind == self._param.VAR_POSITIONAL

    @property
    def has_default_value(
        self
    ) -> bool:
        return self._param.default is not self._param.empty

    @property
    def default_value(
        self
    ) -> Any:
        return self._param.default

    def __str__(
        self
    ) -> str:
        s = self._display_name
        if self._real_name != self._display_name:
            s += f' (bound to {self._real_name})'

        return s

    def __repr__(
        self
    ) -> str:
        return f'<{self.__class__.__qualname__} [{str(self)}]>'
