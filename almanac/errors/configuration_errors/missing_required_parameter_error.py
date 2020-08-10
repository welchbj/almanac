from .base_configuration_error import BaseConfigurationError


class MissingRequiredParameterError(BaseConfigurationError):
    """An exception type for missing configuration parameters."""
