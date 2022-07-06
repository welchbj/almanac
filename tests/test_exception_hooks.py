"""Tests for application event hooking."""

import pytest

from almanac import (
    ConflictingExceptionCallbacksError,
    current_app,
    InvalidCallbackTypeError,
    MissingRequiredParameterError,
)

from .utils import get_test_app


@pytest.mark.asyncio
async def test_exception_hook_resolution_order():
    class ExcA(Exception):
        pass

    class ExcB(ExcA):
        pass

    class ExcC(ExcB):
        pass

    class ExcD(Exception):
        pass

    app = get_test_app()

    app.bag.last_hook = "X"

    @app.hook.exception(ExcA)
    async def hook_A(exc):
        current_app().bag.last_hook = "A"
        assert type(exc) == ExcA
        assert exc.args[0] == "A"

    @app.hook.exception(ExcB)
    async def hook_B(exc):
        current_app().bag.last_hook = "B"
        assert type(exc) == ExcB
        assert exc.args[0] == "B"

    @app.hook.exception(ExcC)
    async def hook_C(exc):
        current_app().bag.last_hook = "C"
        assert type(exc) == ExcC
        assert exc.args[0] == "C"

    @app.hook.exception(Exception)
    async def catch_all_hook(exc):
        current_app().bag.lask_hook = "D"
        assert type(exc) == ExcD
        assert exc.args[0] == "D"

    @app.cmd.register()
    async def raise_A():
        raise ExcA("A")

    @app.cmd.register()
    async def raise_B():
        raise ExcB("B")

    @app.cmd.register()
    async def raise_C():
        raise ExcC("C")

    @app.cmd.register()
    async def raise_D():
        raise ExcD("D")

    await app.eval_line("raise_A")
    assert app.bag.last_hook == "A"

    app.bag.last_hook = "X"

    await app.eval_line("raise_B")
    assert app.bag.last_hook == "B"

    app.bag.last_hook = "X"

    await app.eval_line("raise_C")
    assert app.bag.last_hook == "C"


@pytest.mark.asyncio
async def test_multi_exception_hook():
    class ExcA(Exception):
        pass

    class ExcB(Exception):
        pass

    app = get_test_app()

    app.bag.exc_list = []

    @app.hook.exception(ExcA, ExcB)
    async def handle_A_and_B(ecx):
        app = current_app()

        if isinstance(ecx, ExcA):
            app.bag.exc_list.append("A")
        elif isinstance(ecx, ExcB):
            app.bag.exc_list.append("B")
        else:
            assert False, "this should not happen"

    @app.cmd.register()
    async def raise_A():
        raise ExcA()

    @app.cmd.register()
    async def raise_B():
        raise ExcB()

    await app.eval_line("raise_A")
    await app.eval_line("raise_B")

    assert app.bag.exc_list == ["A", "B"]


@pytest.mark.asyncio
async def test_empty_exception_decorator():
    app = get_test_app()

    with pytest.raises(MissingRequiredParameterError):

        @app.hook.exception()
        async def dummy():
            pass


@pytest.mark.asyncio
async def test_invalid_exception_hook_type():
    app = get_test_app()

    with pytest.raises(InvalidCallbackTypeError):

        @app.hook.exception(Exception)
        def sync_hook(exc):
            pass


@pytest.mark.asyncio
async def test_exception_hook_overwrite():
    app = get_test_app()

    app.bag.marker = "xxx"

    @app.hook.exception(Exception)
    async def hook_exc_one(exc):
        app = current_app()
        app.bag.marker = "one"

    with pytest.raises(ConflictingExceptionCallbacksError):

        @app.hook.exception(Exception)
        async def dummy(exc):
            pass

    @app.hook.exception(Exception, allow_overwrite=True)
    async def hook_exc_two(exc):
        app = current_app()
        app.bag.marker = "two"

    @app.cmd.register()
    async def raise_exc():
        raise RuntimeError()

    await app.eval_line("raise_exc")
    assert app.bag.marker == "two"


@pytest.mark.asyncio
async def test_hooking_exceptions_from_command_hooks():
    class ExcBefore(Exception):
        pass

    class ExcAfter(Exception):
        pass

    app = get_test_app()

    app.bag.did_hook_before = False
    app.bag.did_hook_after = False

    @app.cmd.register()
    async def hook_me_before():
        pass

    @app.hook.before("hook_me_before")
    async def raise_exc_before():
        raise ExcBefore()

    @app.hook.exception(ExcBefore)
    async def hook_exc_before(exc: ExcBefore):
        assert type(exc) == ExcBefore
        current_app().bag.did_hook_before = True

    @app.cmd.register()
    async def hook_me_after():
        pass

    @app.hook.after("hook_me_after")
    async def raise_exc_after():
        raise ExcAfter("after")

    @app.hook.exception(ExcAfter)
    async def hook_exc_after(exc: ExcAfter):
        assert type(exc) == ExcAfter
        current_app().bag.did_hook_after = True

    await app.eval_line("hook_me_before")
    await app.eval_line("hook_me_after")

    assert app.bag.did_hook_after is True
    assert app.bag.did_hook_before is True


@pytest.mark.asyncio
async def test_hooking_exceptions_from_init_and_exit_callbacks():
    class ExcInit(Exception):
        pass

    class ExcExit(Exception):
        pass

    app = get_test_app()
    app.bag.did_hook_on_init = False
    app.bag.did_hook_on_exit = False

    @app.hook.exception(ExcInit)
    async def hook_ExcInit(exc: ExcInit):
        assert type(exc) == ExcInit
        current_app().bag.did_hook_on_init = True

    @app.hook.exception(ExcExit)
    async def hook_ExcExit(exc: ExcExit):
        assert type(exc) == ExcExit
        current_app().bag.did_hook_on_exit = True

    @app.on_init()
    async def raise_init_error():
        raise ExcInit()

    @app.on_exit()
    async def raise_exit_error():
        raise ExcExit()

    await app.run_on_init_callbacks()
    await app.run_on_exit_callbacks()

    assert app.bag.did_hook_on_init is True
    assert app.bag.did_hook_on_exit is True
