"""A WordCompleter that works properly with almanac's command grammar."""

from typing import Callable, Iterable, List, Union

from prompt_toolkit.completion import CompleteEvent, Completion, Completer
from prompt_toolkit.document import Document

from ..parsing import parse_cmd_line, last_incomplete_token


class WordCompleter(Completer):
    """A WordCompleter that works properly with almanac's command grammar.

    This class is necessary due to the way that the prompt toolkit WordCompleter relies
    on filtering based on the current word under the cursor, which will break in
    scenarios in the almanac grammar when trying to yield completion values for
    a key=val input (since the word under the cursor is "key=val").

    """

    def __init__(
        self,
        words: Union[List[str], Callable[[], List[str]]]
    ) -> None:
        self._words = words

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        words = self._words
        if callable(words):
            words = words()

        parse_status = parse_cmd_line(document.text)
        last_token = last_incomplete_token(document, parse_status.unparsed_text)

        needle = last_token.value
        for word in words:
            if word.startswith(needle):
                yield Completion(word, start_position=-len(needle))
