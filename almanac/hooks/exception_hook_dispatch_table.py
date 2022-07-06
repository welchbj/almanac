import inspect

from typing import Callable, MutableMapping, Optional, Type

from .assertions import assert_async_callback
from .types import AsyncExceptionHookCallback
from ..errors import (
    ConflictingExceptionCallbacksError,
    InvalidCallbackTypeError,
    MissingRequiredParameterError,
)


_HookMapping = MutableMapping[Type[Exception], AsyncExceptionHookCallback]


class ExceptionHookDispatchTable:
    """A table for storing and dispatching exception hooks."""

    def __init__(self) -> None:
        self._callback_table: _HookMapping = {}

    def __call__(
        self, *exception_types: Type[Exception], allow_overwrite: bool = False
    ) -> Callable[[AsyncExceptionHookCallback], AsyncExceptionHookCallback]:
        """A decorator for adding a callback for when exceptions occur."""

        if not exception_types:
            raise MissingRequiredParameterError(
                "Must specify at least one exception_type"
            )

        def decorator(
            hook_coro: AsyncExceptionHookCallback,
        ) -> AsyncExceptionHookCallback:
            for exc_type in exception_types:
                self.set_hook_for_exc_type(
                    exc_type, hook_coro, allow_overwrite=allow_overwrite
                )

            return hook_coro

        return decorator

    def set_hook_for_exc_type(
        self,
        exc_type: Type[Exception],
        hook_coro: AsyncExceptionHookCallback,
        allow_overwrite: bool = False,
    ) -> None:
        """Set a hook for an exception type."""
        try:
            assert_async_callback(hook_coro)
        except InvalidCallbackTypeError as e:
            raise e

        if exc_type in self._callback_table.keys() and not allow_overwrite:
            raise ConflictingExceptionCallbacksError(
                "Attempted to overwrite existing exception handler for "
                f"{exc_type} without explicit allow_overwrite=True"
            )

        self._callback_table[exc_type] = hook_coro

    def get_hook_for_exc_type(
        self, exc_type: Type[Exception]
    ) -> Optional[AsyncExceptionHookCallback]:
        """Return all matching hooks for the specified exception type."""
        matching_hook: Optional[AsyncExceptionHookCallback] = None
        min_mro_dist = float("inf")

        # Look for the registered exception type that is "closest" in the class
        # hierarchy to the exception type we are resolving.
        for registered_exc_type, hook_coro in self._callback_table.items():
            test_min_mro_dist = _mro_distance(exc_type, registered_exc_type)
            if test_min_mro_dist < min_mro_dist:
                min_mro_dist = test_min_mro_dist
                matching_hook = hook_coro

        return matching_hook


def _mro_distance(sub_cls: Type, super_cls: Type) -> float:
    try:
        sub_cls_mro = inspect.getmro(sub_cls)
        return sub_cls_mro.index(super_cls)
    except ValueError:
        return float("inf")
