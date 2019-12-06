"""Run an example application."""

import asyncio

from almanac import Application


async def main():
    app = Application()
    await app.run()


if __name__ == '__main__':
    asyncio.run(main())
