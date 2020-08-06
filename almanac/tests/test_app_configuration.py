"""Tests for application configuration."""

from unittest import IsolatedAsyncioTestCase

from almanac import (
    ConflictingPromoterTypesError,
    current_app,
    InvalidCallbackTypeError
)

from .utils import AlmanacTextMixin


class TestAppConfiguration(IsolatedAsyncioTestCase, AlmanacTextMixin):

    async def test_prompt_str_customization(self):
        app = self.get_test_app()
        app.bag.counter = 0

        @app.prompt_str()
        def inc_prompt():
            inner_app_ref = current_app()
            inner_app_ref.bag.counter += 1
            return f'{inner_app_ref.bag.counter}> '

        self.assertEqual(app.current_prompt_str, '1> ')
        self.assertEqual(app.current_prompt_str, '2> ')
        self.assertEqual(app.current_prompt_str, '3> ')

    async def test_invalid_prompt_str_callback(self):
        app = self.get_test_app()

        with self.assertRaises(InvalidCallbackTypeError):
            @app.prompt_str()
            async def async_callback():
                return 'prompt> '

    async def test_exit_callback(self):
        app = self.get_test_app()
        app.bag.exit_count = 0

        register_exit_callback = app.on_exit()

        async def inc_counter():
            inner_app_ref = current_app()
            inner_app_ref.bag.exit_count += 1

        for i in range(5):
            register_exit_callback(inc_counter)

        await app.run_on_exit_callbacks()
        self.assertEqual(app.bag.exit_count, 5)

    async def test_invalid_exit_callback(self):
        app = self.get_test_app()

        with self.assertRaises(InvalidCallbackTypeError):
            @app.on_exit()
            def sync_callback():
                pass

    async def test_init_callback(self):
        app = self.get_test_app()
        app.bag.init_count = 0

        register_init_callback = app.on_init()

        async def inc_counter():
            inner_app_ref = current_app()
            inner_app_ref.bag.init_count += 1

        for i in range(5):
            register_init_callback(inc_counter)

        await app.run_on_init_callbacks()
        self.assertEqual(app.bag.init_count, 5)

    async def test_invalid_init_callback(self):
        app = self.get_test_app()

        with self.assertRaises(InvalidCallbackTypeError):
            @app.on_init()
            def sync_callback():
                pass

    async def test_conflicting_type_promoters(self):
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
