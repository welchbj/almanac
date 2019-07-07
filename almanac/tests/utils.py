"""Utilities for testing ``almanac``."""

import trio


def async_test(coro):
    """Decoractor for async tests.

    See:
        https://stackoverflow.com/a/46324983/5094008

    """
    def wrapper(*args, **kwargs):
        return trio.run(coro(*args, **kwargs))
    return wrapper
