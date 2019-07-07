"""Implementation of the ``TomlPageProvider`` class."""

import toml

from typing import (
    Any,
    Iterator,
    MutableMapping)

from .abstract_toml_page_serializer_mixin import (
    AbstractTomlPageSerializerMixin)
from ..abstract_page import (
    AbstractPage)
from ..abstract_page_provider import (
    AbstractPageProvider)
from ...loaders import (
    AbstractTextResourceLoader)


class TomlPageProvider(AbstractPageProvider):
    """A page provider that can load/dump pages from/to TOML text."""

    def __init__(
        self,
        text_loader: AbstractTextResourceLoader,
        serializer: AbstractTomlPageSerializerMixin
    ) -> None:
        self._text_loader = text_loader
        self._serializer = serializer

    def provide_pages(
        self
    ) -> Iterator[AbstractPage]:
        toml_dict: MutableMapping[str, Any]
        toml_dict = toml.loads(self.text_loader.load_text())
        # TODO

    @property
    def text_loader(
        self
    ) -> AbstractTextResourceLoader:
        """The textual resource loader that provides the TOML."""
        return self._text_loader

    @property
    def serializer(
        self
    ) -> AbstractTomlPageSerializerMixin:
        return self._serializer
