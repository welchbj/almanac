"""Tests for application configuration."""

from unittest import TestCase

from almanac import Application
from almanac import ConflictingPromoterTypesError


class TestAppConfiguration(TestCase):

    def test_conflicting_type_promoters(self):
        app = Application()
        app.add_promoter_for_type(bool, bool)

        with self.assertRaises(ConflictingPromoterTypesError):
            app.add_promoter_for_type(bool, str)

        app = Application()
        app.add_promoter_for_type(int, str)

        with self.assertRaises(ConflictingPromoterTypesError):
            @app.promoter_for(int)
            def promoter_callback(x: int) -> str:
                return str(x)
