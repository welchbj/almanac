"""Implementation of the ``CommandCompleter`` class."""

from __future__ import annotations

from typing import Any, Iterable, TYPE_CHECKING

from prompt_toolkit.document import Document
from prompt_toolkit.completion import (
    CompleteEvent,
    Completion,
    Completer,
    merge_completers
)

from ..commands import FrozenCommand
from ..parsing import IncompleteToken, last_incomplete_token, parse_cmd_line, ParseState
from ..types import is_matching_type

if TYPE_CHECKING:
    from .application import Application


def _startswith_completions(
    needle: str,
    corpus: Iterable[str]
) -> Iterable[Completion]:
    """Utility for yielding Completions that start with a specified word."""
    for candidate in corpus:
        if candidate.startswith(needle):
            yield Completion(candidate, start_position=-len(needle))


class CommandCompleter(Completer):
    """A completer that provides command argument completion for an application."""

    def __init__(
        self,
        app: Application
    ) -> None:
        self._app = app
        self._command_engine = app.command_engine

    def _maybe_complete_for_type(
        self,
        annotation: Any,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        for _type, completers in self._app.type_completer_mapping.items():
            if is_matching_type(_type, annotation):
                yield from merge_completers(completers).get_completions(
                    document, complete_event
                )

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        cmd_line = document.text
        curr_word = document.get_word_before_cursor()

        parse_results, unparsed_text, _, parse_status = parse_cmd_line(cmd_line)

        # Determine if we are in the command name, in which case we can fall back on
        # the CommandEngine for finding potential command names or aliases.
        stripped_cmd_line = cmd_line.strip()
        if parse_status == ParseState.NONE and stripped_cmd_line:
            # There is non-whitespace, and the parser still fails. The line is
            # inherently malformed, so any further completions would just build on that.
            return
        elif not stripped_cmd_line or curr_word == parse_results.command:
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

        args = [x for x in parse_results.positionals]
        kwargs, _ = command.resolved_kwarg_names(parse_results.kv.asDict())

        # Check if we want to avoid binding this argument, since we might not know if
        # really a positional argument or actually an incomplete keyword argument.
        if args and last_token.is_ambiguous_arg and last_token.value == args[-1]:
            args.pop()

        # Determine what would be the unbound arguments if we attempted to bind the
        # current state of the arguments to the command's underlying coroutine. These
        # are our options for future argument-based completions.
        unbound_arguments = command.get_unbound_arguments(*args, **kwargs)
        unbound_kw_args = [x for x in unbound_arguments if not x.is_pos_only]
        unbound_kw_arg_display_names = set(x.display_name for x in unbound_kw_args)
        unbound_pos_args = [x for x in unbound_arguments if not x.is_kw_only]

        could_be_key_or_pos_value = (
            last_token.is_ambiguous_arg and curr_word == last_token.key
        )

        # Yield keyword argument name completions.
        if could_be_key_or_pos_value:
            corpus = [f'{x.display_name}=' for x in unbound_kw_args]
            yield from _startswith_completions(last_token.key, corpus)

        # Yield possible values for the next positional argument.
        if unbound_pos_args and (could_be_key_or_pos_value or last_token.is_pos_arg):
            next_pos_arg = unbound_pos_args[0]

            # Completions from any per-argument registered completer.
            for completer in next_pos_arg.completers:
                yield from self._app.call_as_current_app(
                    completer.get_completions, document, complete_event
                )

            # Completions from any matching application-global type completers.
            yield from self._app.call_as_current_app(
                self._maybe_complete_for_type,
                next_pos_arg.annotation, document, complete_event
            )

        # Yield possible values for the current keyword argument.
        kwarg_name = last_token.key
        if last_token.is_kw_arg and kwarg_name in unbound_kw_arg_display_names:
            matching_kw_arg = command[kwarg_name]

            # Completions from any per-argument registered completer.
            for completer in matching_kw_arg.completers:
                yield from self._app.call_as_current_app(
                    completer.get_completions, document, complete_event
                )

            # Completions from any matching application-global type completers.
            yield from self._app.call_as_current_app(
                self._maybe_complete_for_type,
                matching_kw_arg.annotation, document, complete_event
            )

        # TODO: completions based on the history of the argument?
        #       will probably be a mechanism implemented on the CommandEngine

        # TODO: if we want to inject global styles into the completions generated here,
        #       I think we will need some kind of Completion.replace function, and
        #       re-write properties of each Completion as we yield them
