"""Tests for execution of various command lines."""

import pytest

from almanac import (
    MissingArgumentsError,
    NoSuchArgumentError,
    TooManyPositionalArgumentsError,
)

from .utils import get_test_app


@pytest.mark.asyncio
async def test_simple_type_promotion():
    app = get_test_app()
    app.add_promoter_for_type(int, bool)

    @app.cmd.register()
    async def cmd(arg: int):
        assert type(arg) == bool
        assert arg is True

    await app.eval_line("cmd arg=1")


@pytest.mark.asyncio
async def test_var_args_type_promotions():
    app = get_test_app()
    app.add_promoter_for_type(int, str)

    @app.cmd.register()
    async def cmd_var_pos_args(*args: int):
        for i, x in enumerate(args):
            assert type(x) == str
            assert x == str(i)

    await app.eval_line("cmd_var_pos_args 0 1 2 3 4 5")

    @app.cmd.register()
    async def cmd_var_kw_args(**kwargs: int):
        for key, val in kwargs.items():
            assert type(val) == str
            assert val == "18"

    await app.eval_line("cmd_var_kw_args one=18 two=18 three=18")


@pytest.mark.asyncio
async def test_missing_pos_args():
    app = get_test_app(propagate_runtime_exceptions=True)

    @app.cmd.register()
    async def some_command(arg1: int, arg2: int, arg3: int = 3, *, arg4: int):
        pass

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command 1 arg3=3 arg4=4")
    assert ctx.value.missing_args == ("arg2",)

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command 1")
    assert ctx.value.missing_args == (
        "arg2",
        "arg4",
    )

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command arg4=4")
    assert ctx.value.missing_args == (
        "arg1",
        "arg2",
    )


@pytest.mark.asyncio
async def test_missing_kw_args():
    app = get_test_app(propagate_runtime_exceptions=True)

    @app.cmd.register()
    async def some_command(arg1: int, arg2: int = 2, *, arg3: int, arg4: int):
        pass

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command 1 arg3=3")
    assert ctx.value.missing_args == ("arg4",)

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command 1 arg4=4")
    assert ctx.value.missing_args == ("arg3",)

    with pytest.raises(MissingArgumentsError) as ctx:
        await app.eval_line("some_command 1 arg2=2")
    assert ctx.value.missing_args == (
        "arg3",
        "arg4",
    )


@pytest.mark.asyncio
async def test_too_many_pos_args():
    app = get_test_app(null_output=False, propagate_runtime_exceptions=True)

    @app.cmd.register()
    async def some_command(arg1: int, arg2: int, arg3: int = 3, *, arg4: int):
        pass

    with pytest.raises(TooManyPositionalArgumentsError) as ctx:
        await app.eval_line("some_command 1 2 3 4 arg4=4")
    assert ctx.value.values == (4,)

    with pytest.raises(TooManyPositionalArgumentsError) as ctx:
        await app.eval_line("some_command 1 2 3 4 5 arg4=4")
    assert ctx.value.values == (
        4,
        5,
    )


@pytest.mark.asyncio
async def test_extra_kw_args():
    app = get_test_app(propagate_runtime_exceptions=True)

    @app.cmd.register()
    @app.arg.a(name="A")
    async def some_command(a: int, b: str, x: bool = False):
        pass

    with pytest.raises(NoSuchArgumentError) as ctx:
        await app.eval_line('some_command a=1 b="a string" x=False')
    assert ctx.value.names == ("a",)

    with pytest.raises(NoSuchArgumentError) as ctx:
        await app.eval_line('some_command A=1 a=1 b="a string" x=False')
    assert ctx.value.names == ("a",)

    with pytest.raises(NoSuchArgumentError) as ctx:
        await app.eval_line("some_command A=1 b=2 c=3 x=True y=4 z=[1,2,3]")
    assert ctx.value.names == (
        "c",
        "y",
        "z",
    )
