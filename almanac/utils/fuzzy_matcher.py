"""Implementation of the ``FuzzyMatcher`` class."""

from collections import (
    namedtuple)
from difflib import (
    SequenceMatcher)
from operator import (
    attrgetter)
from typing import (
    Iterable,
    Iterator,
    Tuple)


FuzzResult = namedtuple('FuzzResult', ['string', 'ratio'])

_DEFAULT_FUZZ_RATIO_THRESHOLD = 0.6
_DEFAULT_MAX_MATCHES = 3


class FuzzyMatcher:
    """A simple fuzzy string matcher.

    Attributes:
        reference: The string against which candidate matches are compared.
        candidates: The strings to compare against ``reference``.
        ratio_threshold: The float within the range 0 < r < 1 that valid
            matches must surpass when compared to ``reference``.
        num_max_matches: The maximum number of matches that this class will
            hold.

    Notes:
        The ``candidates`` iterable will be consumed upon initialization.

    """

    def __init__(
        self,
        reference: str,
        candidates: Iterable[str],
        ratio_threshold: float = _DEFAULT_FUZZ_RATIO_THRESHOLD,
        num_max_matches: int = _DEFAULT_MAX_MATCHES
    ) -> None:
        self._reference: str = reference

        _fuzzes = iter(self.__class__.fuzz(reference, c) for c in candidates)
        _passing_fuzzes = iter(f for f in _fuzzes if f.ratio > ratio_threshold)
        _sorted_passing_fuzzes = tuple(
            sorted(_passing_fuzzes, key=attrgetter('ratio')))

        if len(_sorted_passing_fuzzes) <= num_max_matches:
            self._results = _sorted_passing_fuzzes
        else:
            self._results = _sorted_passing_fuzzes[:num_max_matches]

        self._matches = tuple(r.string for r in self._results)

    @staticmethod
    def fuzz(
        reference: str,
        comparison: str
    ) -> float:
        """Return the fuzz ratio of two strings. Higher means more similar."""
        ratio = SequenceMatcher(None, reference, comparison).ratio()
        return FuzzResult(comparison, ratio)

    @property
    def reference(
        self
    ) -> str:
        """The reference string against which candidates are matched."""
        return self._reference

    @property
    def matches(
        self
    ) -> Tuple[str, ...]:
        """Only the strings of matching candidates."""
        return self._matches

    @property
    def results(
        self
    ) -> Tuple[FuzzResult, ...]:
        """The `FuzzResult` result of each match."""
        return self._results

    def __bool__(
        self
    ) -> bool:
        return bool(self._matches)

    def __iter__(
        self
    ) -> Iterator[str]:
        yield from self._matches

    def __contains__(
        self,
        s: str
    ) -> bool:
        return s in self._matches
