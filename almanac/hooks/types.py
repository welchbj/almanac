from typing import Any, Callable, Coroutine, Protocol, TypeVar, Union

from prompt_toolkit.formatted_text import FormattedText

# In the future, would like to make AsyncHookCallback a generic protocol-based type. In
# the meantime, we'll settle for the ambiguous return type of Any.
#
# Seems to depend on this issue:
# https://github.com/python/mypy/issues/5876
AsyncHookCallback = Callable[..., Coroutine[Any, Any, Any]]

_T = TypeVar("_T", covariant=True)


class PromoterFunction(Protocol[_T]):
    def __call__(self, __raw_value: Any) -> _T:
        ...


class AsyncNoArgsCallback(Protocol[_T]):
    def __call__(self) -> Coroutine[Any, Any, _T]:
        ...


class SyncNoArgsCallback(Protocol[_T]):
    def __call__(self) -> _T:
        ...


class AsyncExceptionHookCallback(Protocol):
    # mypy does not seem to respect trying to annotate __exc with Exception, so we
    # leave it as Any for now.
    def __call__(self, __exc: Any) -> Coroutine[Any, Any, Any]:
        ...


PromptCallback = SyncNoArgsCallback[Union[str, FormattedText]]
