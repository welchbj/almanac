"""Exception type for attempting to map multiple promoters to one type."""

from .base_configuration_error import BaseConfigurationError


class ConflictingPromoterTypesError(BaseConfigurationError):
    """An exception type for attempting to map multiple promoters to one type."""
