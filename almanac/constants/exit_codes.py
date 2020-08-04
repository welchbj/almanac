"""Exit code constants."""

from enum import auto, IntEnum, unique


@unique
class ExitCodes(IntEnum):
    OK = 0

    ERR_COMMAND_PARSING = auto()
    ERR_COMMAND_INVALID_ARGUMENTS = auto()
    ERR_COMMAND_NONEXISTENT = auto()

    ERR_RUNTIME_EXC = auto()
