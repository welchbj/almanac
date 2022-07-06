from __future__ import annotations

from typing import Any, Callable, Coroutine

CommandCoroutine = Callable[..., Coroutine[Any, Any, int]]
