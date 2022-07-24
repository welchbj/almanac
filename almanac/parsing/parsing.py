# The parsing logic is heavily borrowed from the python-nubia project, available at:
# https://github.com/facebookincubator/python-nubia
#
# In compliance with python-nubia's BSD-style license, its copyright and license terms
# are included below:
#
# BSD License
#
# For python-nubia software
#
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name Facebook nor the names of its contributors may be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
from enum import Enum, auto
from functools import lru_cache
from typing import NamedTuple

import pyparsing as pp
from prompt_toolkit.document import Document

from almanac.errors import PartialParseError, TotalParseError


class Patterns:
    ALLOWED_SYMBOLS_IN_STRING = r"-_/#@£$€%*+~|<>?."
    IDENTIFIER = r"([a-zA-Z_][a-zA-Z0-9_\-]*)"
    WHITESPACE = r"\s+"

    UNQUOTED_STRING = r"([a-zA-Z0-9" + ALLOWED_SYMBOLS_IN_STRING + r"]+)"
    STRING_SINGLE_QUOTE = r"\'([^\\\']|\\.)*\'"
    STRING_DOUBLE_QUOTE = r"\"([^\\\"]|\\.)*\""

    BOOLEAN = r"(True|true|False|false)"
    FLOAT = r"\-?\d+\.\d*([eE]\d+)?"
    INTEGER = r"\-?\d+"

    KWARG = IDENTIFIER + r"(\s*=\s*)"
    COMMAND = r"^" + IDENTIFIER + r"(\s+|$)"

    @staticmethod
    def is_valid_identifier(s: str) -> bool:
        """Whether the specified string is a valid command name or kwarg identifier."""
        return bool(re.fullmatch(Patterns.IDENTIFIER, s))


def _no_transform(x):
    return x


def _bool_transform(x):
    return x in (
        "True",
        "true",
    )


def _str_transform(x):
    return x.strip("\"'")


_TRANSFORMS = {
    "bool": _bool_transform,
    "str": _str_transform,
    "int": int,
    "float": float,
    "dict": dict,
}


def _parse_type(data_type):
    transform = _TRANSFORMS.get(data_type, _no_transform)

    def _parse(s, loc, toks):
        return [transform(x) for x in toks]

    return _parse


# Valid identifiers cannot start with a number, but may contain them in their body.
identifier = pp.Word(pp.alphas + "_-", pp.alphanums + "_-")

# XXX: allow for hex?
int_value = pp.Regex(Patterns.INTEGER).setParseAction(_parse_type("int"))

float_value = pp.Regex(Patterns.FLOAT).setParseAction(_parse_type("float"))

bool_value = (
    pp.Literal("True") ^ pp.Literal("true") ^ pp.Literal("False") ^ pp.Literal("false")
).setParseAction(_parse_type("bool"))

quoted_string = pp.quotedString.setParseAction(_parse_type("str"))

unquoted_string = pp.Word(
    pp.alphanums + Patterns.ALLOWED_SYMBOLS_IN_STRING
).setParseAction(_parse_type("str"))

string_value = quoted_string | unquoted_string

single_value = bool_value | float_value | int_value | string_value

list_value = pp.Group(
    pp.Suppress("[") + pp.Optional(pp.delimitedList(single_value)) + pp.Suppress("]")
).setParseAction(_parse_type("list"))

dict_value = pp.Forward()

value = list_value ^ single_value ^ dict_value

dict_key_value = pp.dictOf(string_value + pp.Suppress(":"), value)

dict_value << pp.Group(
    pp.Suppress("{") + pp.delimitedList(dict_key_value) + pp.Suppress("}")
).setParseAction(_parse_type("dict"))

# Positionals must be end of line or has a space (or more) afterwards.
# This is to ensure that the parser treats text like "something=" as invalid
# instead of parsing this as positional "something" and leaving the "=" as
# invalid on its own.
positionals = pp.ZeroOrMore(
    value + (pp.StringEnd() | pp.Suppress(pp.OneOrMore(pp.White())))
).setResultsName("positionals")

key_value = pp.Dict(
    pp.ZeroOrMore(pp.Group(identifier + pp.Suppress("=") + value))
).setResultsName("kv")

command = identifier.setResultsName("command")

command_line = command + positionals + key_value


class ParseState(Enum):
    FULL = auto()
    PARTIAL = auto()
    NONE = auto()


class ParseStatus(NamedTuple):
    results: pp.ParseResults
    unparsed_text: str
    unparsed_start_pos: int
    state: ParseState


@lru_cache()
def parse_cmd_line(text: str) -> ParseStatus:
    """Attempt to parse a command line, returning a :class:`ParseStatus` object."""
    try:
        parse_results = _raw_parse_cmd_line(text)
        unparsed_text = ""
        unparsed_start_pos = len(text)
        parse_state = ParseState.FULL
    except PartialParseError as e:
        parse_results = e.partial_result
        unparsed_text = e.remaining
        unparsed_start_pos = e.error_pos
        parse_state = ParseState.PARTIAL
    except TotalParseError:
        parse_results = None
        unparsed_text = text
        unparsed_start_pos = 0
        parse_state = ParseState.NONE

    return ParseStatus(parse_results, unparsed_text, unparsed_start_pos, parse_state)


def _raw_parse_cmd_line(text: str) -> pp.ParseResults:
    """Attempt to parse the command line as per the grammar defined in this module.

    If the specified text can be fully parsed, then a `pypaysing.ParseResults` will be
    returned with the following attributes:

        * command: The name or alias of the command.
        * kv: A dictionary of key-value pairs representing the keyword arguments.
        * positionals: Any positional argument values.

    Otherwise, a descendant of :class:`CommandParseError` is raised.

    Raises:
        :class:`CommandPartialParseError`: If the specified text can be partially
            parsed, but errors still exist.
        :class:`CommandPartialParseError`: If the text cannot even be partially parsed.

    """
    try:
        result = command_line.parseString(text, parseAll=True)
        return result
    except pp.ParseException as e:
        remaining = e.markInputline()
        remaining = remaining[(remaining.find(">!<") + 3) :]

        try:
            partial_result = command_line.parseString(text, parseAll=False)
        except pp.ParseException as ee:
            raise TotalParseError(str(ee)) from None

        new_exc = PartialParseError(str(e), remaining, partial_result, e.col)
        raise new_exc from None


class IncompleteToken:
    """Encapsulation of a token that could only be partially parsed."""

    def __init__(self, token: str) -> None:
        self._token = token

        self._key = ""
        self._value = ""
        self._is_kw_arg = False
        self._is_pos_arg = False

        self._parse()

    def _parse(self) -> None:
        key, delim, value = self._token.partition("=")

        if any(x in key for x in "[]{}\"'"):
            # Treat the whole token as a positional value.
            self._is_pos_arg = True
            self._value = self._token
            return

        if delim == "=":
            # This is a key=value.
            self._is_kw_arg = True
            self._key = key
            self._value = value
        else:
            # This could either be the beginning of something like key=value or the
            # positional literal keywest.
            self._key = self._value = key

    @property
    def is_kw_arg(self) -> bool:
        return self._is_kw_arg

    @property
    def is_pos_arg(self) -> bool:
        return self._is_pos_arg

    @property
    def is_ambiguous_arg(self) -> bool:
        return not self._is_kw_arg and not self._is_pos_arg

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        if self.is_kw_arg:
            return f"kwarg {self._key}={self._value}"
        elif self.is_pos_arg:
            return f"positional {self._value}"
        elif self.is_ambiguous_arg:
            return f"ambiguous {self._key}"
        else:
            return "Parse error"

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} [{str(self)}]>"


def last_incomplete_token(document: Document, unparsed_text: str) -> IncompleteToken:
    if document.char_before_cursor in " ]}":
        last_token = ""
    else:
        last_space = document.find_backwards(" ", in_current_line=True)
        if last_space is None:
            last_space = -1

        last_token = document.text[last_space + 1 :]

    # The longer of the last_token and unparsed_text is taken in the event that the
    # unparsed_text is an open literal, which could itself contain spaces.
    if len(unparsed_text) > len(last_token):
        last_token = unparsed_text

    return IncompleteToken(last_token)


def last_incomplete_token_from_document(document: Document) -> IncompleteToken:
    """Shortcut for getting the last incomplete token only from a ``Document``."""
    parse_status = parse_cmd_line(document.text)
    return last_incomplete_token(document, parse_status.unparsed_text)
