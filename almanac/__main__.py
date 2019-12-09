"""Run an example application."""

import asyncio

from almanac import make_standard_app


async def main():
    app = make_standard_app()

    @app.command
    async def liteval(app, io, opts) -> int:
        """Literal eval of Python code.

        Usage:
            liteval <expr>

        """
        # TODO
        io.print_info('Called liteval')
        return 0

    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
