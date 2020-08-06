"""Tests for application event hooking."""

from unittest import IsolatedAsyncioTestCase

from almanac import (
    current_app,
    InvalidCallbackTypeError,
    NoSuchCommandError,
    PagePath
)

from .utils import AlmanacTextMixin


class TestAppConfiguration(IsolatedAsyncioTestCase, AlmanacTextMixin):

    async def test_before_and_after_command_hooks(self):
        app = self.get_test_app()

        app.bag.values = []

        @app.hook.before('cd')
        async def before_cd_hook_one(path: PagePath):
            self.assertIsInstance(path, PagePath)
            self.assertEqual(path, '/')
            current_app().bag.values.append(1)

        @app.hook.before('cd')
        async def before_cd_hook_two(path: PagePath):
            self.assertIsInstance(path, PagePath)
            self.assertEqual(path, '/')
            current_app().bag.values.append(2)

        @app.hook.after('cd')
        async def after_cd_hook_one(path: PagePath):
            self.assertIsInstance(path, PagePath)
            self.assertEqual(path, '/')
            current_app().bag.values.append(3)

        @app.hook.after('cd')
        async def after_cd_hook_two(path: PagePath):
            self.assertIsInstance(path, PagePath)
            self.assertEqual(path, '/')
            current_app().bag.values.append(4)

        await app.eval_line('cd /')

    async def test_hook_registration_on_frozen_command(self):
        app = self.get_test_app()

        app.bag.before = []
        app.bag.values = []
        app.bag.after = []

        @app.cmd.register()
        async def my_command(x: int):
            current_app().bag.values.append(x)

        @app.hook.before(my_command)
        async def before_my_command(x: int):
            current_app().bag.before.append(x)

        @app.hook.after(my_command)
        async def after_my_command(x: int):
            current_app().bag.after.append(x)

        await app.eval_line('my_command 1')
        await app.eval_line('my_command 2')
        await app.eval_line('my_command 3')

        self.assertListEqual(app.bag.before, [1, 2, 3])
        self.assertListEqual(app.bag.values, [1, 2, 3])
        self.assertListEqual(app.bag.after, [1, 2, 3])

    async def test_invalid_command_hook_types(self):
        app = self.get_test_app()

        with self.assertRaises(InvalidCallbackTypeError):
            @app.hook.before('ls')
            def bad_sync_hook_one():
                pass

        with self.assertRaises(InvalidCallbackTypeError):
            @app.hook.after('ls')
            def bad_sync_hook_two():
                pass

    async def test_non_existent_command_hook_registration(self):
        app = self.get_test_app()

        with self.assertRaises(NoSuchCommandError):
            @app.hook.before('not_real')
            async def dummy_one(path: str):
                pass

        with self.assertRaises(NoSuchCommandError):
            @app.hook.after('not_real')
            async def dummy_two(path: str):
                pass

        @app.cmd.register()
        @app.cmd(name='not_real')
        async def now_im_real():
            pass

        app.bag.before_hook_did_fire = False
        app.bag.after_hook_did_fire = False

        @app.hook.before('not_real')
        async def before_not_real():
            current_app().bag.before_hook_did_fire = True

        @app.hook.after('not_real')
        async def after_not_real():
            current_app().bag.after_hook_did_fire = True

        self.assertFalse(app.bag.before_hook_did_fire)
        self.assertFalse(app.bag.after_hook_did_fire)

        await app.eval_line('not_real')

        self.assertTrue(app.bag.before_hook_did_fire)
        self.assertTrue(app.bag.after_hook_did_fire)
