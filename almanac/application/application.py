"""Implementation of the ``Application`` class."""

from typing import (
    Iterator,
    List,
    Optional)

from prompt_toolkit import (
    PromptSession)
from prompt_toolkit.patch_stdout import (
    patch_stdout)
from ..commands import (
    CommandEngine)
from ..pages import (
    AbstractPageProvider,
    PageNavigator,
    PagePathLike)

# TODO: rather than setting children during the parsing of pages, we will
#       have to pass over the page index and create the relationships once
#       everything has parsed


class Application:
    """The core class of ``almanac``, wrapping everything together.

    Attributes:
        TODO

    TODO: examples

    """

    def __init__(
        self
    ) -> None:
        # TODO: load some configuration options and put them into the session

        self._command_engine = CommandEngine()
        self._page_navigator = PageNavigator()
        self._session = PromptSession(
            message=self._prompt_callback,
            # completer=TODO
            complete_while_typing=True,
            complete_in_thread=True)

    @property
    def page_navigator(
        self
    ) -> PageNavigator:
        """The :class:`PageNavigator` powering this app's navigation."""
        return self._page_navigator

    async def eval_line(
        self,
        line: str
    ) -> None:
        """Evaluate a line passed to the application by the user."""
        # TODO
        print('You said:', line)

    async def run(
        self
    ) -> int:
        """Run the application's event loop.

        Returns:
            The exit code of the application's execution.

        """
        with patch_stdout():
            while True:
                try:
                    line = await self._session.prompt_async(
                        completer=self._command_engine,
                        complete_while_typing=True,
                        complete_in_thread=True)

                    line = line.strip()
                    if not line:
                        continue

                    await self.eval_line(line)
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                finally:
                    # TODO: this needs to clean up running tasks
                    pass

            return 0

    def _prompt_callback(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self._page_navigator.current_page.get_prompt()
