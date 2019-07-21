from .back import (  # noqa
    BackCommand)
from .cd import (  # noqa
    CdCommand)
from .echo import (  # noqa
    EchoCommand)
from .encode import (  # noqa
    EncodeCommand)
from .forward import (  # noqa
    ForwardCommand)
from .ls import (  # noqa
    LsCommand)
from .pwd import (  # noqa
    PwdCommand)
from .search import (  # noqa
    SearchCommand)

BUILTIN_COMMANDS = (
    BackCommand(),
    CdCommand(),
    EchoCommand(),
    EncodeCommand(),
    ForwardCommand(),
    LsCommand(),
    PwdCommand(),
    SearchCommand(),)
