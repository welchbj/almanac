from pathlib import PurePosixPath
from typing import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer
from prompt_toolkit.completion.base import Completion
from prompt_toolkit.document import Document

from ..context import current_app
from ..errors import BasePageError
from ..parsing import last_incomplete_token_from_document


class PagePathCompleter(Completer):
    """A completer for paths to an application's pages."""

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        app = current_app()

        last_token = last_incomplete_token_from_document(document)
        typed_path = last_token.value

        if typed_path.endswith("/"):
            complete_from_dir = typed_path
            stem = ""
        else:
            posix_path = PurePosixPath(typed_path)
            complete_from_dir = str(posix_path.parent)
            stem = posix_path.stem

        try:
            page = app.page_navigator[complete_from_dir]
        except BasePageError:
            return

        for child_page in page.children:
            candidate_page_name = child_page.path.segments[-1]
            if candidate_page_name.startswith(stem):
                yield Completion(candidate_page_name, start_position=-len(stem))
