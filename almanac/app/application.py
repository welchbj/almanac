"""Implementation of the ``Application`` class."""

from typing import (
    Iterator,
    List,
    Optional)

from prompt_toolkit import (
    PromptSession)
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion)
from prompt_toolkit.document import (
    Document)
from trio import (
    open_nursery)
from trio._core._run import (
    Nursery)

from ..commands import (
    AbstractCommand,
    CommandEngine)
from ..pages import (
    AbstractPageProvider,
    PageNavigator,
    PagePathLike)
from ..shell import (
    EvaluationContext,
    Shlexer)

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
        self._command_engine = CommandEngine()
        self._nursey: Optional[Nursery] = None
        self._page_navigator = PageNavigator()
        self._session = PromptSession(message=self._prompt_callback)

    @property
    def pages(
        self
    ) -> PageNavigator:
        """The :class:`PageNavigator` powering this app's navigation."""
        return self._page_navigator

    async def eval_line(
        self,
        line: str
    ) -> None:
        """Evaluate a line passed to the application by the user."""
        shlexer: Shlexer = self.get_shlexer(line)
        if not shlexer.did_parse_succeed:
            # TODO: report why we can't / won't run this
            return

        for command_run_coro in shlexer.wrapped_run_coros:
            self._nursery.start_soon(command_run_coro)

    async def run(
        self
    ) -> int:
        """Run the application's event loop.

        Returns:
            The exit code of the application's execution.

        """
        async with open_nursery() as nursery:
            self._nursey = nursery

            while True:
                try:
                    line = self._session.prompt(
                        completer=self._command_engine,
                        complete_while_typing=True,
                        complete_in_thread=True).strip()

                    if not line:
                        continue

                    await self.eval_line(line)
                except KeyboardInterrupt:
                    # TODO: this needs to clean up running tasks
                    continue
                except EOFError:
                    break
                finally:
                    # TODO: is anything needed here?
                    pass

        self._nursey = None
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
        """Yield completions from a :class:`Shlexer`."""
        text = document.text.strip()
        shlexer = self.get_shlexer(text)
        yield from shlexer.get_completions()

    def get_shlexer(
        self,
        s: str
    ) -> Shlexer:
        """Get a :class:`Shlexer` from the app's current state.

        Args:
            s: The command to parse.

        """
        evaluation_context = EvaluationContext(self)
        self._page_navigator.current_page.mutate_base_evaluation_context(
            evaluation_context)

        return Shlexer(s, self, self._command_engine, evaluation_context)

    def _prompt_callback(
        self
    ) -> str:
        """A callback for getting the current page's prompt."""
        return self._page_navigator.current_page.get_prompt()
