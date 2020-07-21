"""Command parsing implementation."""

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

import pyparsing as pp

from ..errors import CommandParseError

allowed_symbols_in_string = r'-_/#@£$€%*+~|<>?.'


def _no_transform(x):
    return x


def _bool_transform(x):
    return x in ('True', 'true',)


def _str_transform(x):
    return x.strip('"\'')


_TRANSFORMS = {
    'bool': _bool_transform,
    'str': _str_transform,
    'int': int,
    'float': float,
    'dict': dict,
}


def _parse_type(data_type):
    transform = _TRANSFORMS.get(data_type, _no_transform)

    def _parse(s, loc, toks):
        return [transform(x) for x in toks]

    return _parse


# Valid identifiers cannot start with a number, but may contain them in their body.
identifier = pp.Word(pp.alphas + '_-', pp.alphanums + '_-')

# XXX: allow for hex?
int_value = pp.Regex(r'\-?\d+').setParseAction(_parse_type('int'))

float_value = pp.Regex(r'\-?\d+\.\d*([eE]\d+)?').setParseAction(_parse_type('float'))

bool_value = (
    pp.Literal('True') ^ pp.Literal('true') ^
    pp.Literal('False') ^ pp.Literal('false')
).setParseAction(_parse_type('bool'))

quoted_string = pp.quotedString.setParseAction(_parse_type('str'))

unquoted_string = pp.Word(
    pp.alphanums + allowed_symbols_in_string
).setParseAction(_parse_type('str'))

string_value = quoted_string | unquoted_string

single_value = bool_value | float_value | string_value | int_value

list_value = pp.Group(
    pp.Suppress('[') +
    pp.Optional(pp.delimitedList(single_value)) +
    pp.Suppress(']')
).setParseAction(_parse_type('list'))

dict_value = pp.Forward()

value = list_value ^ single_value ^ dict_value

dict_key_value = pp.dictOf(string_value + pp.Suppress(':'), value)

dict_value << pp.Group(
    pp.Suppress('{') + pp.delimitedList(dict_key_value) + pp.Suppress('}')
).setParseAction(_parse_type('dict'))

# Positionals must be end of line or has a space (or more) afterwards.
# This is to ensure that the parser treats text like "something=" as invalid
# instead of parsing this as positional "something" and leaving the "=" as
# invalid on its own.
positionals = pp.ZeroOrMore(
    value + (pp.StringEnd() ^ pp.Suppress(pp.OneOrMore(pp.White())))
).setResultsName('positionals')

key_value = pp.Dict(pp.ZeroOrMore(pp.Group(
    identifier + pp.Suppress('=') + value
))).setResultsName('kv')

command = identifier.setResultsName('command')

command_line = command + key_value + positionals


def parse(
    text: str
) -> pp.ParseResults:
    try:
        result = command_line.parseString(text, parseAll=True)
        return result
    except pp.ParseException as e:
        remaining = e.markInputline()
        remaining = remaining[(remaining.find('>!<') + 3):]
        partial_result = command_line.parseString(text, parseAll=False)

        new_exc = CommandParseError(str(e), remaining, partial_result, e.col)
        raise new_exc from e
