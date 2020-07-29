"""Styles for almanac applications."""

from prompt_toolkit.styles import style_from_pygments_dict
from pygments.token import Keyword, Name, Number, Operator, String, Text


DARK_MODE_STYLE = style_from_pygments_dict({
    Operator: '#C27FF5',

    Name.RealCommand: 'ansimagenta',
    Name.NonexistentCommand: 'ansired',
    Name.Kwarg: 'ansibrightmagenta',

    Keyword.Boolean: 'ansiyellow',
    Number.Integer: 'ansiyellow',
    Number.Float: 'ansiyellow',

    String.SingleQuote: 'ansiyellow',
    String.DoubleQuote: 'ansiyellow',

    Text: '',
})

LIGHT_MODE_STYLE = ...  # TODO
