"""Welcome to a simple interactive HTTP client.

The current URL to request is the application's current path. Directories will be
created as you cd into them.

Here's an example:

    > pwd
    /
    > cd checkip.amazonaws.com
    checkip.amazonaws.com> get
    [*] Sending GET request to https://checkip.amazonaws.com...
    [*] Status 200 response from https://checkip.amazonaws.com
    [*] Here's the content:
    x.x.x.x

    checkip.amazonaws.com> cd ../api.ipify.org
    api.ipify.org> get format=json
    [*] Sending GET request to https://api.ipify.org...
    [*] Status 200 response from https://api.ipify.org/?format=json
    [*] Here's the content:
    {"ip":"x.x.x.x"}

    api.ipify.org> ls /
    /checkip.amazonaws.com
    /api.ipify.org
"""

#
# Install dependencies with:
#
# pip install almanac aiohttp pygments
#

import asyncio
import functools

import aiohttp
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import get_lexer_for_mimetype

from almanac import PagePath, make_standard_app

HTTP_VERBS = ["GET", "POST", "PUT", "OPTIONS"]

app = make_standard_app()


@app.on_init()
async def open_session():
    app.io.raw(__doc__)

    app.bag.session = aiohttp.ClientSession()
    app.io.info("Session opened!")


@app.on_exit()
async def close_session():
    await app.bag.session.close()
    app.io.info("Session closed!")


@app.prompt_text()
def custom_prompt():
    stripped_path = str(app.page_navigator.current_page.path).lstrip("/")
    return f"{stripped_path}> "


@app.hook.before("cd")
async def cd_hook_before(path: PagePath):
    if path not in app.page_navigator:
        app.page_navigator.add_directory_page(path)


@app.hook.exception(aiohttp.ClientError)
async def handle_aiohttp_errors(exc: aiohttp.ClientError):
    app.io.error(f"{exc.__class__.__name__}: {str(exc)}")


# This is the workhorse coroutine. All of the main HTTP request commands in this
# application are partially bound versions of this coroutine.
async def request(*, method: str, proto: str = "https", **params: str):
    """Send an HTTP or HTTPS request."""
    if method not in HTTP_VERBS:
        app.io.error(f"Invalid HTTP verb {method}")

    path = str(app.current_path).lstrip("/")
    url = f"{proto}://{path}"
    app.io.info(f"Sending {method} request to {url}...")

    request_coro = getattr(app.bag.session, method.lower())
    resp = await request_coro(url=url, params=params)
    async with resp:
        try:
            lexer = get_lexer_for_mimetype(resp.content_type)
        except Exception:
            lexer = get_lexer_for_mimetype("text/plain")

        app.io.info(f"Status {resp.status} response from {resp.url}")
        app.io.info("Here's the content:")

        text = await resp.text()
        highlighted_text = highlight(text, lexer, TerminalFormatter())
        app.io.ansi(highlighted_text)


# Since we want to re-use the above request coroutine implementation across several
# different top-level commands (get, put, post, etc.), we compose a decorator with
# the commands' shared configuration, which can later be applied to each of the
# partially-bound coroutines below.
shared_config_decorator = app.cmd.compose(
    app.arg.proto(description="Protocol to use for request.", choices=["http", "https"])
)

# Here, we add some configuration just for the top-level request command.
register_request_command = app.cmd.register(
    shared_config_decorator,
    app.arg.method(description="HTTP verb for request.", choices=HTTP_VERBS),
)
register_request_command(request)

# We next make a slightly-modified version of the request command for each of the main
# HTTP verbs.
for http_verb in HTTP_VERBS:
    partial_request_coro = functools.partial(request, method=http_verb)
    partial_request_coro.__name__ = http_verb.lower()  # type: ignore
    partial_request_coro.__doc__ = f"Make an HTTP {http_verb} request."

    register_func = app.cmd.register(
        shared_config_decorator, app.arg.method(hidden=True)
    )
    register_func(partial_request_coro)

if __name__ == "__main__":
    asyncio.run(app.prompt())
