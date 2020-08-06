"""Implementation of the ``CommandCompleter`` class."""

from __future__ import annotations

import re

from typing import Any, Iterable, TYPE_CHECKING

from prompt_toolkit.document import Document
from prompt_toolkit.completion import (
    CompleteEvent,
    Completion,
    Completer,
    merge_completers
)

from ..arguments import FrozenArgument
from ..commands import FrozenCommand
from ..completion import rewrite_completion_stream
from ..errors import NoSuchArgumentError
from ..parsing import (
    IncompleteToken,
    last_incomplete_token,
    parse_cmd_line,
    ParseState,
    Patterns
)
from ..types import is_matching_type

if TYPE_CHECKING:
    from .application import Application


_compiled_word_re = re.compile(Patterns.UNQUOTED_STRING)


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

    def _get_command_completions(
        self,
        start_of_command: str
    ) -> Iterable[Completion]:
        for name_or_alias in sorted(self._command_engine.keys()):
            if name_or_alias.startswith(start_of_command):
                command = self._command_engine[name_or_alias]

                if name_or_alias == command.name:
                    display_meta = command.abbreviated_description
                else:
                    display_meta = f'(alias for {command.name})'

                yield Completion(
                    name_or_alias,
                    start_position=-len(start_of_command),
                    display_meta=display_meta
                )

    def _get_completions_for_arg(
        self,
        frozen_arg: FrozenArgument,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Completions from any per-argument registered completer.
        for completer in frozen_arg.completers:
            yield from rewrite_completion_stream(
                self._app.call_as_current_app_sync(
                    completer.get_completions,
                    document, complete_event
                ),
                display_meta='From per-argument completer.'
            )

        # Completions from any matching application-global type completers.
        yield from rewrite_completion_stream(
            self._app.call_as_current_app_sync(
                self._maybe_complete_for_type,
                frozen_arg.annotation, document, complete_event
            ),
            display_meta='From global per-type completer.'
        )

    def _get_kw_arg_name_completions(
        self,
        start_of_kw_arg: str,
        unbound_kw_args: Iterable[FrozenArgument]
    ) -> Iterable[Completion]:
        candidate_args = [
            x for x in unbound_kw_args if not x.hidden and not x.is_var_kw
        ]
        for candidate_arg in sorted(candidate_args, key=lambda x: x.display_name):
            if candidate_arg.display_name.startswith(start_of_kw_arg):
                text = f'{candidate_arg.display_name}='
                meta = candidate_arg.abbreviated_description

                yield Completion(
                    text,
                    start_position=-len(start_of_kw_arg),
                    display_meta=meta
                )

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        cmd_line = document.text
        curr_word = document.get_word_before_cursor(pattern=_compiled_word_re)

        parse_results, unparsed_text, _, parse_status = parse_cmd_line(cmd_line)

        # Determine if we are in the command name, in which case we can fall back on
        # the CommandEngine for finding potential command names or aliases.
        stripped_cmd_line = cmd_line.strip()
        if parse_status == ParseState.NONE and stripped_cmd_line:
            # There is non-whitespace, and the parser still fails. The line is
            # inherently malformed, so any further completions would just build on that.
            return
        elif not stripped_cmd_line or curr_word == parse_results.command:
            yield from self._get_command_completions(curr_word)
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
        unbound_pos_args = [x for x in unbound_arguments if not x.is_kw_only]

        could_be_key_or_pos_value = (
            last_token.is_ambiguous_arg and curr_word == last_token.key
        )

        # Yield keyword argument name completions.
        if could_be_key_or_pos_value:
            yield from self._get_kw_arg_name_completions(
                last_token.key, unbound_kw_args
            )

        # Yield possible values for the next positional argument.
        if unbound_pos_args and (could_be_key_or_pos_value or last_token.is_pos_arg):
            next_pos_arg = unbound_pos_args[0]
            yield from self._get_completions_for_arg(
                next_pos_arg, document, complete_event
            )

        # Yield possible values for the current keyword argument.
        kwarg_name = last_token.key
        if last_token.is_kw_arg:
            try:
                matching_kw_arg = command[kwarg_name]
                yield from self._get_completions_for_arg(
                    matching_kw_arg, document, complete_event
                )
            except NoSuchArgumentError:
                pass

        # TODO: completions based on the history of the argument?
        #       will probably be a mechanism implemented on the CommandEngine

        # TODO: if we want to inject global styles into the completions generated here,
        #       I think we will need some kind of Completion.replace function, and
        #       re-write properties of each Completion as we yield them
