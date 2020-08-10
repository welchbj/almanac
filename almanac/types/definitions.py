from __future__ import annotations

from typing import Any, Coroutine, Callable

CommandCoroutine = Callable[..., Coroutine[Any, Any, int]]
