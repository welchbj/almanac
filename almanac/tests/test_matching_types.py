"""Tests for comparisons between types."""

from typing import Union
from unittest import TestCase

from almanac import is_matching_type


class TestMatchingTypes(TestCase):
    """Tests for comparisons between types."""

    def test_union(self):
        self.assertTrue(
            is_matching_type(int, Union[int, str])
        )
