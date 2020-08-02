"""A completer for page paths."""

from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer
from prompt_toolkit.completion.base import Completion
from prompt_toolkit.document import Document


class PagePathCompleter(Completer):
    """A completer for paths to an application's pages."""

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # TODO

        return []
