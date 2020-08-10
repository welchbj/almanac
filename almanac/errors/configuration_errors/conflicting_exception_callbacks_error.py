from .base_configuration_error import BaseConfigurationError


class ConflictingExceptionCallbacksError(BaseConfigurationError):
    """Exception type for trying to implicitly overwrite an exception hook callback."""
