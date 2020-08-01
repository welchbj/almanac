"""Tests for application configuration."""

from unittest import TestCase

from almanac import ConflictingPromoterTypesError

from .utils import AlmanacTextMixin


class TestAppConfiguration(TestCase, AlmanacTextMixin):

    def test_conflicting_type_promoters(self):
        app = self.get_test_app()
        app.add_promoter_for_type(bool, bool)

        with self.assertRaises(ConflictingPromoterTypesError):
            app.add_promoter_for_type(bool, str)

        app = self.get_test_app()
        app.add_promoter_for_type(int, str)

        with self.assertRaises(ConflictingPromoterTypesError):
            @app.promoter_for(int)
            def promoter_callback(x: int) -> str:
                return str(x)
