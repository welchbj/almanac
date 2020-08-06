"""Welcome to a simple interactive HTTP client.

The current URL to request is the application's current path. Directories will be
created as you cd into them.
"""

#
# Install dependencies with:
#
# pip install almanac aiohttp pygments
#

import aiohttp
import asyncio

from almanac import highlight_for_mimetype, make_standard_app, PagePath

app = make_standard_app()


@app.on_init()
async def runs_at_start_up():
    app.io.raw(__doc__)

    app.bag.session = aiohttp.ClientSession()
    app.io.info('Session opened!')


@app.on_exit()
async def runs_at_shut_down():
    await app.bag.session.close()
    app.io.info('Session closed!')


@app.prompt_text()
def custom_prompt():
    stripped_path = str(app.page_navigator.current_page.path).lstrip('/')
    return f'{stripped_path}> '


@app.hook.before('cd')
async def cd_hook_before(path: PagePath):
    if path not in app.page_navigator:
        app.page_navigator.add_directory_page(path)


@app.hook.exception(aiohttp.ClientError)
async def handle_aiohttp_errors(exc: aiohttp.ClientError):
    app.io.error(f'{exc.__class__.__name__}: {str(exc)}')


@app.cmd.register()
@app.arg.method(choices=['GET', 'POST', 'PUT'], description='HTTP verb for request.')
@app.arg.proto(choices=['http', 'https'], description='Protocol for request.')
async def request(method: str, *, proto: str = 'https', **params: str):
    """Send an HTTP or HTTPS request."""
    path = str(app.current_path).lstrip('/')
    url = f'{proto}://{path}'
    app.io.info(f'Sending {method} request to {url}...')

    resp = await app.bag.session.request(method, url, params=params)
    async with resp:
        text = await resp.text()
        highlighted_text = highlight_for_mimetype(text, resp.content_type)

        app.io.info(f'Status {resp.status} response from {resp.url}')
        app.io.info('Here\'s the content:')
        app.io.ansi(highlighted_text)


if __name__ == '__main__':
    asyncio.run(app.prompt())
