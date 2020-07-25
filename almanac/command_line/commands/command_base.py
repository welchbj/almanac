"""Implementation of the ``Command`` class."""

from __future__ import annotations

import inspect
import itertools

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Tuple, Union

from ..types import CommandCoroutine
from ...constants import CommandLineDefaults


class CommandBase(ABC):
    """Encapsulation of a command."""

    def __init__(
        self,
        coroutine: CommandCoroutine,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[Union[str, Iterable[str]]] = None
    ) -> None:
        self._name = name if name is not None else coroutine.__name__

        if description is not None:
            self._description = description
        elif (maybe_doc := coroutine.__doc__) is not None:
            self._description = maybe_doc
        else:
            self._description = CommandLineDefaults.DOC

        self._aliases: List[str] = []
        if isinstance(aliases, str):
            self._aliases.append(aliases)
        elif aliases is not None:
            self._aliases.extend(aliases)

        self._impl_signature = inspect.signature(coroutine)
        self._impl_coroutine = coroutine

    @property
    def name(
        self
    ) -> str:
        """The primary name of this function."""
        return self._name

    @name.setter
    def name(
        self,
        new_name: str
    ) -> None:
        self._abstract_name_setter(new_name)

    @abstractmethod
    def _abstract_name_setter(
        self,
        new_name: str
    ) -> None:
        """Abstract name setter to allow for access control."""

    @property
    def description(
        self
    ) -> str:
        """A description for this command."""
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
    def aliases(
        self
    ) -> Tuple[str, ...]:
        """Aliases for this command."""
        return tuple(self._aliases)

    @abstractmethod
    def add_alias(
        self,
        *aliases: str
    ) -> None:
        """Abstract alias appender to allow for access control."""

    @property
    def identifiers(
        self
    ) -> Tuple[str, ...]:
        """A combination of this command's name and any of its aliases."""
        return tuple(itertools.chain(
            (self._name,),
            self._aliases
        ))

    @property
    def signature(
        self
    ) -> inspect.Signature:
        """The signature of the user-written coroutine wrapped by this command."""
        return self._impl_signature

    @property
    def coroutine(
        self
    ) -> CommandCoroutine:
        """The internal coroutine that this command wraps."""
        return self._impl_coroutine
