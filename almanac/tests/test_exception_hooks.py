"""Tests for application event hooking."""

from unittest import IsolatedAsyncioTestCase

from almanac import (
    ConflictingExceptionCallbacksError,
    current_app,
    InvalidCallbackTypeError,
    MissingRequiredParameterError
)

from .utils import AlmanacTextMixin


class TestAppConfiguration(IsolatedAsyncioTestCase, AlmanacTextMixin):

    async def test_exception_hook_resolution_order(self):
        class ExcA(Exception):
            pass

        class ExcB(ExcA):
            pass

        class ExcC(ExcB):
            pass

        class ExcD(Exception):
            pass

        app = self.get_test_app()

        app.bag.last_hook = 'X'

        @app.hook.exception(ExcA)
        async def hook_A(exc):
            current_app().bag.last_hook = 'A'
            self.assertIsInstance(exc, ExcA)
            self.assertEqual(exc.args[0], 'A')

        @app.hook.exception(ExcB)
        async def hook_B(exc):
            current_app().bag.last_hook = 'B'
            self.assertIsInstance(exc, ExcB)
            self.assertEqual(exc.args[0], 'B')

        @app.hook.exception(ExcC)
        async def hook_C(exc):
            current_app().bag.last_hook = 'C'
            self.assertIsInstance(exc, ExcC)
            self.assertEqual(exc.args[0], 'C')

        @app.hook.exception(Exception)
        async def catch_all_hook(exc):
            current_app().bag.lask_hook = 'D'
            self.assertIsInstance(exc, ExcD)
            self.assertEqual(exc.args[0], 'D')

        @app.cmd.register()
        async def raise_A():
            raise ExcA('A')

        @app.cmd.register()
        async def raise_B():
            raise ExcB('B')

        @app.cmd.register()
        async def raise_C():
            raise ExcC('C')

        @app.cmd.register()
        async def raise_D():
            raise ExcD('D')

        await app.eval_line('raise_A')
        self.assertEqual(app.bag.last_hook, 'A')

        app.bag.last_hook = 'X'

        await app.eval_line('raise_B')
        self.assertEqual(app.bag.last_hook, 'B')

        app.bag.last_hook = 'X'

        await app.eval_line('raise_C')
        self.assertEqual(app.bag.last_hook, 'C')

    async def test_multi_exception_hook(self):
        class ExcA(Exception):
            pass

        class ExcB(Exception):
            pass

        app = self.get_test_app()

        app.bag.exc_list = []

        @app.hook.exception(ExcA, ExcB)
        async def handle_A_and_B(ecx):
            app = current_app()

            if isinstance(ecx, ExcA):
                app.bag.exc_list.append('A')
            elif isinstance(ecx, ExcB):
                app.bag.exc_list.append('B')
            else:
                assert False, 'this should not happen'

        @app.cmd.register()
        async def raise_A():
            raise ExcA()

        @app.cmd.register()
        async def raise_B():
            raise ExcB()

        await app.eval_line('raise_A')
        await app.eval_line('raise_B')

        self.assertListEqual(app.bag.exc_list, ['A', 'B'])

    async def test_empty_exception_decorator(self):
        app = self.get_test_app()

        with self.assertRaises(MissingRequiredParameterError):
            @app.hook.exception()
            async def dummy():
                pass

    async def test_invalid_exception_hook_type(self):
        app = self.get_test_app()

        with self.assertRaises(InvalidCallbackTypeError):
            @app.hook.exception(Exception)
            def sync_hook(exc):
                pass

    async def test_exception_hook_overwrite(self):
        app = self.get_test_app()

        app.bag.marker = 'xxx'

        @app.hook.exception(Exception)
        async def hook_exc_one(exc):
            app = current_app()
            app.bag.marker = 'one'

        with self.assertRaises(ConflictingExceptionCallbacksError):
            @app.hook.exception(Exception)
            async def dummy(exc):
                pass

        @app.hook.exception(Exception, allow_overwrite=True)
        async def hook_exc_two(exc):
            app = current_app()
            app.bag.marker = 'two'

        @app.cmd.register()
        async def raise_exc():
            raise RuntimeError()

        await app.eval_line('raise_exc')
        self.assertEqual(app.bag.marker, 'two')
