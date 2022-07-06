from prompt_toolkit.styles import style_from_pygments_dict
from pygments.token import Keyword, Name, Number, Operator, String, Text


DARK_MODE_STYLE = style_from_pygments_dict(
    {
        Operator: "ansicyan",
        Name.RealCommand: "ansimagenta",
        Name.NonexistentCommand: "ansired",
        Name.Kwarg: "ansibrightmagenta",
        Keyword.Boolean: "ansibrightyellow",
        Number.Integer: "ansiyellow",
        Number.Float: "ansiyellow",
        String.SingleQuote: "ansibrightgreen",
        String.DoubleQuote: "ansibrightgreen",
        Text: "",
    }
)

LIGHT_MODE_STYLE = ...  # TODO
