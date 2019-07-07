"""Implementation of the ``AbstractTextResourceLoader``."""

from abc import (
    ABC,
    abstractmethod)


class AbstractTextResourceLoader(ABC):
    """An interface for loading textual resources."""

    @abstractmethod
    def load_text(
        self
    ) -> str:
        """Load and return the text that the implementation provides."""
