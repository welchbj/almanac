"""Utilities for iteration."""

from itertools import tee
from typing import Iterable, Iterator, Tuple, TypeVar

T = TypeVar('T')


def pairwise(
    i: Iterable[T]
) -> Iterator[Tuple[T, T]]:
    """Move over an iterable, two at a time.

    .. code-block:: python

        >>> from almanac import pairwise
        >>> for pair in pairwise([1, 2, 3, 4]):
        ...     print(pair)
        (1, 2)
        (2, 3)
        (3, 4)

    See:
        https://docs.python.org/3/library/itertools.html#itertools-recipes

    """
    a, b = tee(i)
    next(b, None)
    return zip(a, b)
