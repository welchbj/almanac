"""Run an example application."""

import ast
import asyncio

from typing import Optional

from almanac import current_app, make_standard_app
from prompt_toolkit.completion import WordCompleter


async def main():
    app = make_standard_app()

    @app.command(aliases=['leval'])
    @app.aliases('literal_eval', 'eval')
    @app.completer('expr', WordCompleter(['0x10', '["a"]']))
    async def liteval(
        expr: str, verbose: Optional[bool] = False
    ) -> int:
        """Evaluation of a Python literal."""
        app = current_app()

        if verbose:
            app.io.print_info('Verbose mode is on!')

        app.io.print_raw(ast.literal_eval(expr))
        return 0

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
