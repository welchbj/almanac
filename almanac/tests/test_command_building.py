"""Tests for various command/argument generation error conditions."""

from unittest import IsolatedAsyncioTestCase

from prompt_toolkit.completion import DummyCompleter

from almanac import Application
from almanac import (
    CommandRegistrationError,
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

            @app.command()
            @app.arg('b', name='c')
            async def f(a: int):
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.command
            @app.arg_name('a', 'b')
            async def h(_a: int):
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.command()
            @app.arg_description('b', 'c')
            async def i():
                pass

        with self.assertRaises(NoSuchArgumentError):
            app = Application()

            @app.command()
            @app.arg_completer('c', completer=DummyCompleter())
            @app.arg('a', completer=DummyCompleter())
            async def j(a: int, b: str):
                pass

    async def test_invalid_name_identifiers(self):
        """Test attempting to set cmd/arg names to invalid identifiers."""
        # TODO

    async def test_improper_decorator_ordering(self):
        """Test putting the app.command decorator in invalid locations."""
        with self.assertRaises(CommandRegistrationError):
            app = Application()

            @app.cmd_name('another_name')
            @app.command()
            async def cmd():
                pass

    async def test_invalid_command_function(self):
        """Test trying to mark the command coroutine as a regular function."""
        with self.assertRaises(CommandRegistrationError):
            app = Application()

            @app.command()
            def f():
                pass
