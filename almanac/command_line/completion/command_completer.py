"""Implementation of the ``CommandCompleter`` class."""

from __future__ import annotations

from enum import auto, Enum
from typing import Iterable, TYPE_CHECKING

from prompt_toolkit.document import Document
from prompt_toolkit.completion import (
    CompleteEvent,
    Completion,
    Completer,
)

from ..commands import FrozenCommand
from ..parsing import IncompleteToken, last_incomplete_token, parse_cmd_line
from ...errors import PartialParseError, TotalParseError

if TYPE_CHECKING:
    from ...core import Application


def _startswith_completions(
    needle: str,
    corpus: Iterable[str]
) -> Iterable[Completion]:
    """Utility for yielding Completions that start with a specified word."""
    for candidate in corpus:
        if candidate.startswith(needle):
            yield Completion(candidate, start_position=-len(needle))


class _ParseStatus(Enum):
    FULL = auto()
    PARTIAL = auto()
    NONE = auto()


class CommandCompleter(Completer):

    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app
        self._command_engine = app.command_engine

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        cmd_line = document.text
        curr_word = document.get_word_before_cursor()

        try:
            parse_results = parse_cmd_line(cmd_line)
            unparsed_text = ''
            parse_status = _ParseStatus.FULL
        except PartialParseError as e:
            parse_results = e.partial_result
            unparsed_text = e.remaining
            parse_status = _ParseStatus.PARTIAL
        except TotalParseError:
            parse_results = None
            unparsed_text = cmd_line
            parse_status = _ParseStatus.NONE

        # XXX
        print('parse_results:')
        print(parse_results.asDict())
        print('curr_word:')
        print(curr_word)
        print('parse progress:')
        print(parse_status)

        # Determine if we are in the command name, in which case we can fall back on
        # the CommandEngine for finding potential command names or aliases.
        if parse_status == _ParseStatus.NONE or curr_word == parse_results.command:
            yield from _startswith_completions(curr_word, self._command_engine.keys())
            return

        # Figure out what command we are working with.
        try:
            command: FrozenCommand = self._command_engine[parse_results.command]
        except KeyError:
            # Not a real command name, so we can't provide completions for it.
            return

        # Determine the last incomplete token.
        last_token: IncompleteToken = last_incomplete_token(document, unparsed_text)

        # XXX
        print('last_token:')
        print(last_token)

        args = [x for x in parse_results.positionals]
        kwargs = command.resolved_kwarg_names(parse_results.kv.asDict())

        # Check if we want to avoid binding this argument, since we might not know if
        # really a positional argument or actually an incomplete keyword argument.
        if args and last_token.is_ambiguous_arg and last_token.value == args[-1]:
            args.pop()

        # Determine what would be the unbound arguments if we attempted to bind the
        # current state of the arguments to the command's underlying coroutine. These
        # are our options for future argument-based completions.
        unbound_arguments = command.get_unbound_arguments(*args, **kwargs)
        unbound_kw_args = [x for x in unbound_arguments if not x.is_pos_only]
        unbound_pos_args = [x for x in unbound_arguments if not x.is_kw_only]

        # XXX
        print('unbound_arguments:')
        print(unbound_arguments)

        could_be_key_or_pos_value = (
            last_token.is_ambiguous_arg and curr_word == last_token.key
        )

        # Yield keyword argument name completions. The second part of this Boolean
        # clause prevents offering completions in scenarios immediately following a
        # literal, like [].
        if could_be_key_or_pos_value:
            corpus = [f'{x.display_name}=' for x in unbound_kw_args]
            yield from _startswith_completions(last_token.key, corpus)

        # Yield possible values for the next positional argument.
        if could_be_key_or_pos_value or last_token.is_pos_arg:
            # TODO: how do we get the nth pos argument?

            # TODO: get completions based on per-argument completer
            # TODO: get completions based on history of argument
            # TODO: get completions if configured as global type
            pass

        # Yield possible values for the current keyword argument.
        if last_token.is_kw_arg:
            # TODO: get completions based on per-argument completer
            # TODO: get completions based on history of argument
            # TODO: get completions if configured as global type
            pass
