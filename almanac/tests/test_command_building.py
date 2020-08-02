"""Tests for various command/argument generation error conditions."""

from unittest import IsolatedAsyncioTestCase

from prompt_toolkit.completion import DummyCompleter

from almanac import Application
from almanac import (
    CommandRegistrationError,
    InvalidArgumentNameError,
    NoSuchArgumentError,
)


class TestCommandBuilding(IsolatedAsyncioTestCase):

    async def test_command_property_construction(self):
        # TODO
        pass

    async def test_argument_property_construction(self):
        # TODO
        pass

    async def test_invalid_argument_names(self):
        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.cmd.register()
            @app.arg.b(name='c')
            async def f(a: int):
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.cmd.register()
            @app.arg.a(name='b')
            async def h(_a: int):
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.cmd.register()
            @app.arg.b(description='c')
            async def i():
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.cmd.register()
            @app.arg.c(completers=DummyCompleter())
            @app.arg.a(completers=DummyCompleter())
            async def j(a: int, b: str):
                pass

    async def test_invalid_name_identifiers(self):
        """Test attempting to set cmd/arg names to invalid identifiers."""
        with self.assertRaises(InvalidArgumentNameError):
            app = Application()

            @app.cmd.register()
            @app.cmd(name='invalid identifier')
            async def a():
                pass

        with self.assertRaises(InvalidArgumentNameError):
            app = Application()

            @app.cmd.register()
            @app.cmd(name='invalid identifier')
            async def b():
                pass

    async def test_improper_decorator_ordering(self):
        """Test putting the app.command decorator in invalid locations."""
        with self.assertRaises(CommandRegistrationError):
            app = Application()

            @app.cmd(name='another_name')
            @app.cmd.register()
            async def cmd():
                pass

    async def test_invalid_command_function(self):
        """Test trying to mark the command coroutine as a regular function."""
        with self.assertRaises(CommandRegistrationError):
            app = Application()

            @app.cmd.register()
            def f():
                pass
