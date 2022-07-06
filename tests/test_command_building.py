"""Tests for various command/argument generation error conditions."""

import pytest
from prompt_toolkit.completion import DummyCompleter

from almanac import (
    Application,
    ArgumentNameCollisionError,
    CommandNameCollisionError,
    CommandRegistrationError,
    InvalidArgumentNameError,
    NoSuchArgumentError,
)


@pytest.mark.asyncio
async def test_colliding_argument_names():
    app = Application()

    with pytest.raises(ArgumentNameCollisionError) as ctx:

        @app.cmd.register()
        @app.arg.a(name="b")
        async def one(a: int, b: int):
            pass

    assert ctx.value.names == ("b",)

    with pytest.raises(ArgumentNameCollisionError) as ctx:

        @app.cmd.register()
        @app.arg.a(name="c")
        @app.arg.b(name="c")
        async def two(a: int, b: int):
            pass

    assert ctx.value.names == ("c",)

    with pytest.raises(ArgumentNameCollisionError) as ctx:

        @app.cmd.register()
        @app.arg.a(name="c")
        @app.arg.b(name="d")
        async def three(a: int, b: int, c: int, d: int):
            pass

    assert ctx.value.names == (
        "c",
        "d",
    )


@pytest.mark.asyncio
async def test_colliding_command_names():
    app = Application()

    @app.cmd.register()
    async def a_command():
        pass

    with pytest.raises(CommandNameCollisionError) as ctx:

        @app.cmd.register()
        @app.cmd(name="a_command")
        async def another_command():
            pass

    assert ctx.value.names == ("a_command",)

    with pytest.raises(CommandNameCollisionError) as ctx:

        @app.cmd.register()
        @app.cmd(aliases="a_command")
        async def yet_another_command():
            pass

    assert ctx.value.names == ("a_command",)


@pytest.mark.asyncio
async def test_invalid_argument_names():
    with pytest.raises(NoSuchArgumentError):
        app = Application()

        @app.cmd.register()
        @app.arg.b(name="c")
        async def f(a: int):
            pass

    with pytest.raises(NoSuchArgumentError):
        app = Application()

        @app.cmd.register()
        @app.arg.a(name="b")
        async def h(_a: int):
            pass

    with pytest.raises(NoSuchArgumentError):
        app = Application()

        @app.cmd.register()
        @app.arg.b(description="c")
        async def i():
            pass

    with pytest.raises(NoSuchArgumentError):
        app = Application()

        @app.cmd.register()
        @app.arg.c(completers=DummyCompleter())
        @app.arg.a(completers=DummyCompleter())
        async def j(a: int, b: str):
            pass


@pytest.mark.asyncio
async def test_invalid_name_identifiers():
    """Test attempting to set cmd/arg names to invalid identifiers."""
    with pytest.raises(InvalidArgumentNameError):
        app = Application()

        @app.cmd.register()
        @app.cmd(name="invalid identifier")
        async def a():
            pass

    with pytest.raises(InvalidArgumentNameError):
        app = Application()

        @app.cmd.register()
        @app.cmd(name="invalid identifier")
        async def b():
            pass


@pytest.mark.asyncio
async def test_improper_decorator_ordering():
    """Test putting the app.command decorator in invalid locations."""
    with pytest.raises(CommandRegistrationError):
        app = Application()

        @app.cmd(name="another_name")
        @app.cmd.register()
        async def cmd():
            pass


@pytest.mark.asyncio
async def test_invalid_command_function():
    """Test trying to mark the command coroutine as a regular function."""
    with pytest.raises(CommandRegistrationError):
        app = Application()

        @app.cmd.register()
        def f():
            pass
