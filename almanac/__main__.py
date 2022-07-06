"""Run an example application."""

import ast
import asyncio

from typing import Optional

from almanac import current_app, make_standard_app, WordCompleter


async def main():
    app = make_standard_app()

    @app.cmd.register()
    @app.cmd(aliases=["literal_eval"])
    @app.arg.expr(completers=WordCompleter(["0x10", '["a"]']))
    async def liteval(expr: str, verbose: Optional[bool] = False) -> int:
        """Evaluation of a Python literal."""
        app = current_app()

        if verbose:
            app.io.info("Verbose mode is on!")

        app.io.raw(ast.literal_eval(expr))
        return 0

    await app.prompt()


if __name__ == "__main__":
    asyncio.run(main())
