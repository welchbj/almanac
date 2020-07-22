"""Run an example application."""

import ast
import asyncio

from typing import Optional

from almanac import current_app, make_standard_app


async def main():
    app = make_standard_app()

    @app.command
    async def liteval(expr: str, verbose: Optional[bool] = False) -> int:
        """Literal eval of Python code."""
        app = current_app()

        if verbose:
            app.io.print_info('Verbose mode is on!')

        app.io.print_raw(ast.literal_eval(expr))

        return 0

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
