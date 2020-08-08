"""Tests for comparisons between types."""

from typing import Union

from almanac import is_matching_type


def test_union():
    assert is_matching_type(int, Union[int, str]) is True
