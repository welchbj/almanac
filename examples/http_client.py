"""A simple interactive HTTP client.

Install dependencies with:

    pip install almanac pygments TODO

"""

import asyncio
import functools

from almanac import make_standard_app, PagePathCompleter
from typing import Optional

HTTP_VERBS = ['GET', 'POST', 'PUT', 'OPTIONS']

app = make_standard_app()


async def request(*, method: str, path: Optional[str] = None, protocol: str = 'https'):
    """Send an HTTP or HTTPS request."""
    if path is None:
        # XXX: pull this from the app's current directory path
        app.io.print_err('path not specified')

    url = f'{protocol}://{path}'
    app.io.print_info(f'Sending {method} request to {url}...')

    # TODO


# Since we want to re-use the above request coroutine implementation across several
# different top-level commands (get, put, post, etc.), we compose a decorator with
# the commands' shared configuration, which can later be applied to each of the
# partially-bound coroutines below.
shared_config_decorator = app.cmd.compose(
    app.arg.path(completers=PagePathCompleter()),
    app.arg.protocol(choices=['http', 'https'])
)

# Here, we add some configuration just for the top-level request command.
register_request_command = app.cmd.register(
    shared_config_decorator,
    app.arg.method(choices=HTTP_VERBS),
)
register_request_command(request)

# We next make a slightly-modified version of the request command for each of the main
# HTTP verbs.
for http_verb in HTTP_VERBS:
    partial_request_coro = functools.partial(request, method=http_verb)
    partial_request_coro.__name__ = http_verb.lower()  # type: ignore
    partial_request_coro.__doc__ = f'Make an HTTP {http_verb} request'

    register_func = app.cmd.register(
        shared_config_decorator,
        app.arg.method(hidden=True)
    )
    register_func(partial_request_coro)

if __name__ == '__main__':
    asyncio.run(app.prompt())
