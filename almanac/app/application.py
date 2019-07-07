"""Implementation of the ``Application`` class."""

from typing import (
    Iterator,
    List)

from prompt_toolkit import (
    PromptSession)
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion)
from prompt_toolkit.document import (
    Document)

from ..commands import (
    AbstractCommand,
    CommandEngine)
from ..pages import (
    AbstractPageProvider,
    PageNavigator,
    PagePath,
    PagePathLike)

# TODO: rather than setting children during the parsing of pages, we will
#       have to pass over the page index and create the relationships once
#       everything has parsed

# TODO: we need to think about how the application will handle runtime
#       generation of tasks; this should probably just piggy back off of
#       trio's nursery pattern


class Application(Completer):
    """The core class of ``almanac``, wrapping everything together.

    Attributes:
        TODO

    TODO: examples

    """

    def __init__(
        self
    ) -> None:
        self._page_providers: List[AbstractPageProvider] = []

        # TODO: should we store a trio nursey here, or do we need some kind
        #       of wrapper around the nursey that lets us monitor tasks?

        # TODO: determine if any of below should be publicly exposed
        self._page_navigator = PageNavigator()
        self._session = PromptSession(message=self._prompt_callback)
        self._command_engine = CommandEngine()

    async def eval_line(
        self,
        line: str
    ) -> None:
        """Evaluate a line passed to the application by the user."""
        # TODO

    async def run(
        self
    ) -> int:
        """Run the application's event loop.

        Returns:
            The exit code of the application's execution.

        """
        while True:
            try:
                line = self._session.prompt(
                    completer=self._command_engine,
                    complete_while_typing=True,
                    complete_in_thread=True).strip()

                if not line:
                    continue

                # TODO: there might be a problem with having something other
                #       than the Application be the Completer, since
                #       get_completions is going to be continually called
                #       and is going to rely on the current state of a few
                #       different things (the Shlexer, the CommandEngine, etc.)

                # TODO: we need completion logic from the Shlexer in here;
                #       this is also where we need to pull the base
                #       EvaluationContext from the current page

                await self.eval_line(line)
            except KeyboardInterrupt:
                # TODO: this needs to clean up running tasks
                continue
            except EOFError:
                break
            finally:
                # TODO: is anything needed here?
                pass

        return 0

    def register_command(
        self,
        command: AbstractCommand
    ) -> None:
        """Register a command on this application instance.

        TODO: side effects wrt to auto-completion, etc.

        """
        # TODO: handling duplicates
        self._command_engine.register_command(command)

    def register_page_provider(
        self,
        page_provider: AbstractPageProvider,
        base_path: PagePathLike = '/',
    ) -> None:
        """Register a page provider on this application instance.

        TODO: side effects wrt to page loading

        """
        # TODO
        pass

    async def load_pages(
        self
    ) -> None:
        """TODO."""
        # TODO
        # TODO: diffing against existing pages?

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterator[Completion]:
        """Yield completions from the :class:``CommandEngine``."""
        text = document.text.strip()
        # TODO: what do we pass to the CommandEngine?

    def _prompt_callback(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self._page_navigator.current_page.get_prompt()
