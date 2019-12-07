"""Implementation of the ``AbstractPageProvider`` class."""

from abc import (
    ABC,
    abstractmethod,
    abstractproperty)
from typing import (
    Iterator)

from .abstract_page import (
    AbstractPage)
from .abstract_page_serializer_mixin import (
    AbstractPageSerializerMixin)
from ..loaders import (
    AbstractTextResourceLoader)


class AbstractPageProvider(ABC):
    """The base page provider from which all implementations derive.

    TODO

    """

    @abstractmethod
    def provide_pages(
        self
    ) -> Iterator[AbstractPage]:
        """Provide pages from an external resource."""

    @abstractproperty
    def text_loader(
        self
    ) -> AbstractTextResourceLoader:
        """The textual resource loader that provides the text."""

    @abstractproperty
    def serializer(
        self
    ) -> AbstractPageSerializerMixin:
        """The serializer to convert models to and from text."""
