"""Additional type definitons."""

from typing import Any, Coroutine, Callable


CommandCoroutine = Callable[..., Coroutine[Any, Any, int]]
