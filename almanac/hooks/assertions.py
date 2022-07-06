import asyncio
from typing import Any

from ..errors import InvalidCallbackTypeError


def assert_sync_callback(candidate: Any) -> None:
    """Assert that the candidate is a valid synchronous callback."""
    if not callable(candidate) or asyncio.iscoroutinefunction(candidate):
        raise InvalidCallbackTypeError(f"Invalid synchronous callback {candidate}")


def assert_async_callback(candidate: Any) -> None:
    """Assert that the candidate is a valid asynchronous."""
    if not asyncio.iscoroutinefunction(candidate):
        raise InvalidCallbackTypeError(f"Invalid asynchronous callback {candidate}")
