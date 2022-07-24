from almanac.errors.almanac_error import AlmanacError


class BaseConfigurationError(AlmanacError):
    """The base exception type for configuration errors."""


class ConflictingExceptionCallbacksError(BaseConfigurationError):
    """Exception type for trying to implicitly overwrite an exception hook callback."""


class ConflictingPromoterTypesError(BaseConfigurationError):
    """An exception type for attempting to map multiple promoters to one type."""


class InvalidCallbackTypeError(BaseConfigurationError):
    """An error type for invalid callback types."""


class MissingRequiredParameterError(BaseConfigurationError):
    """An exception type for missing configuration parameters."""
