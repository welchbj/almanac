"""Tests for application configuration."""

import pytest

from almanac import ConflictingPromoterTypesError, InvalidCallbackTypeError, current_app

from .utils import get_test_app


@pytest.mark.asyncio
async def test_prompt_str_customization():
    app = get_test_app()
    app.bag.counter = 0

    @app.prompt_text()
    def inc_prompt():
        inner_app_ref = current_app()
        inner_app_ref.bag.counter += 1
        return f"{inner_app_ref.bag.counter}> "

    assert app.current_prompt_str == "1> "
    assert app.current_prompt_str == "2> "
    assert app.current_prompt_str == "3> "


@pytest.mark.asyncio
async def test_invalid_prompt_str_callback():
    app = get_test_app()

    with pytest.raises(InvalidCallbackTypeError):

        @app.prompt_text()
        async def async_callback():
            return "prompt> "


@pytest.mark.asyncio
async def test_exit_callback():
    app = get_test_app()
    app.bag.exit_count = 0

    register_exit_callback = app.on_exit()

    async def inc_counter():
        inner_app_ref = current_app()
        inner_app_ref.bag.exit_count += 1

    for i in range(5):
        register_exit_callback(inc_counter)

    await app.run_on_exit_callbacks()
    assert app.bag.exit_count == 5


@pytest.mark.asyncio
async def test_invalid_exit_callback():
    app = get_test_app()

    with pytest.raises(InvalidCallbackTypeError):

        @app.on_exit()
        def sync_callback():
            pass


@pytest.mark.asyncio
async def test_init_callback():
    app = get_test_app()
    app.bag.init_count = 0

    register_init_callback = app.on_init()

    async def inc_counter():
        inner_app_ref = current_app()
        inner_app_ref.bag.init_count += 1

    for i in range(5):
        register_init_callback(inc_counter)

    await app.run_on_init_callbacks()
    assert app.bag.init_count == 5


@pytest.mark.asyncio
async def test_invalid_init_callback():
    app = get_test_app()

    with pytest.raises(InvalidCallbackTypeError):

        @app.on_init()
        def sync_callback():
            pass


@pytest.mark.asyncio
async def test_conflicting_type_promoters():
    app = get_test_app()
    app.add_promoter_for_type(bool, bool)

    with pytest.raises(ConflictingPromoterTypesError):
        app.add_promoter_for_type(bool, str)

    app = get_test_app()
    app.add_promoter_for_type(int, str)

    with pytest.raises(ConflictingPromoterTypesError):

        @app.promoter_for(int)
        def promoter_callback(x: int) -> str:
            return str(x)
