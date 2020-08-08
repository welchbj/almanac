"""Tests for application event hooking."""

import pytest

from almanac import (
    current_app,
    InvalidCallbackTypeError,
    NoSuchCommandError,
    PagePath
)

from .utils import get_test_app


@pytest.mark.asyncio
async def test_before_and_after_command_hooks():
    app = get_test_app()

    app.bag.values = []

    @app.hook.before('cd')
    async def before_cd_hook_one(path: PagePath):
        assert type(path) == PagePath
        assert path == '/'
        current_app().bag.values.append(1)

    @app.hook.before('cd')
    async def before_cd_hook_two(path: PagePath):
        assert type(path) == PagePath
        assert path == '/'
        current_app().bag.values.append(2)

    @app.hook.after('cd')
    async def after_cd_hook_one(path: PagePath):
        assert type(path) == PagePath
        assert path == '/'
        current_app().bag.values.append(3)

    @app.hook.after('cd')
    async def after_cd_hook_two(path: PagePath):
        assert type(path) == PagePath
        assert path == '/'
        current_app().bag.values.append(4)

    await app.eval_line('cd /')


@pytest.mark.asyncio
async def test_hook_registration_on_frozen_command():
    app = get_test_app()

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

    assert app.bag.before == [1, 2, 3]
    assert app.bag.values == [1, 2, 3]
    assert app.bag.after == [1, 2, 3]


@pytest.mark.asyncio
async def test_invalid_command_hook_types():
    app = get_test_app()

    with pytest.raises(InvalidCallbackTypeError):
        @app.hook.before('ls')
        def bad_sync_hook_one():
            pass

    with pytest.raises(InvalidCallbackTypeError):
        @app.hook.after('ls')
        def bad_sync_hook_two():
            pass


@pytest.mark.asyncio
async def test_non_existent_command_hook_registration():
    app = get_test_app()

    with pytest.raises(NoSuchCommandError):
        @app.hook.before('not_real')
        async def dummy_one(path: str):
            pass

    with pytest.raises(NoSuchCommandError):
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

    assert app.bag.before_hook_did_fire is False
    assert app.bag.after_hook_did_fire is False

    await app.eval_line('not_real')

    assert app.bag.before_hook_did_fire is True
    assert app.bag.after_hook_did_fire is True  # type:ignore
