"""Run an example application."""

import ast
import asyncio

from almanac import current_app, make_standard_app


async def main():
    app = make_standard_app()

    @app.command
    async def liteval(expr: str) -> int:
        """Literal eval of Python code."""
        app = current_app()

        app.io.print_raw(ast.literal_eval(expr))

        return 0

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
