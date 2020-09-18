<p align="center">
  <img width="600" height="162" src="https://github.com/welchbj/almanac/blob/devel/docs/_static/logo.png?raw=true" alt="almanac logo">
</p>
<p align="center">
  <em>a framework for interactive, page-based console applications</em>
</p>
<p align="center">
  <a href="https://travis-ci.org/welchbj/almanac">
    <img src="https://img.shields.io/travis/welchbj/almanac/devel.svg?style=flat-square&label=linux%20build" alt="linux build status">
  </a>
  <a href="https://ci.appveyor.com/project/welchbj/almanac">
    <img src="https://img.shields.io/appveyor/ci/welchbj/almanac/devel.svg?style=flat-square&label=windows%20build" alt="windows build status">
  </a>
  <a href="https://pypi.org/project/almanac/">
    <img src="https://img.shields.io/pypi/v/almanac.svg?style=flat-square&label=pypi" alt="pypi">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8+-b042f4.svg?style=flat-square" alt="python version">
  </a>
</p>

---

## Synopsis

The `almanac` framework aims to serve as an intuitive interface for spinning up interactive, page-based console applications. Think of it as a Python metaprogramming layer on top of [Python Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) and [Pygments](https://pygments.org/).

## Example

`almanac` turns this:

```python
"""Welcome to a simple interactive HTTP client.

The current URL to request is the application's current path. Directories will be
created as you cd into them.
"""

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
```

Into this:

<p align="center">
  <a href="https://asciinema.org/a/352061?autoplay=1&speed=1.5">
    <img src="https://asciinema.org/a/352061.png" width="750">
  </a>
</p>

## Installation

You can download the latest packaged version from PyPI:

```sh
pip install almanac
```

Alternatively, you can get the bleeding-edge version from version control:

```sh
pip install https://github.com/welchbj/almanac/archive/master.tar.gz
```

## License

The original content of this repository is licensed under the [MIT License](https://opensource.org/licenses/MIT), as per the [LICENSE.txt](./LICENSE.txt) file.

Some of the parsing logic is borrowed from the [python-nubia](https://github.com/facebookincubator/python-nubia) project and is licensed under that project's [BSD License](https://github.com/facebookincubator/python-nubia/blob/master/LICENSE). For more information, please see the comment in [`almanac/parsing/parsing.py`](almanac/parsing/parsing.py).