"""Implementation of the ``TomlPageSerializerMixin``."""

from abc import (
    abstractmethod)

from ..abstract_page_serializer_mixin import (
    AbstractPageSerializerMixin)


class AbstractTomlPageSerializerMixin(AbstractPageSerializerMixin):
    """A mixin for pages that can serialize to/from TOML."""

    @abstractmethod
    def toml_loads(
        self,
        text: str
    ) -> None:
        """Load a model from TOML text."""

    @abstractmethod
    def toml_dumps(
        self
    ) -> str:
        """Dump a model to TOML text."""
