"""Implementation of the ``Shlexer`` class."""

from typing import (
    List,
    Optional)

from .evaluation_context import (
    EvaluationContext)
from .shell_tokens import (
    ShellTokens)
from .shlexer_warning import (
    ShlexerWarning)
from .shtate import (
    Shtate)
from ..commands import (
    CommandEngine)


class Shlexer:
    """A class for lex/parse-ing expressions in the ``almanac`` shell language.

    While the name of this class is ``Shlexer``, you're actually getting a
    parser, too.

    """
    # TODO: idea for parsing stratey and handling nested stuff -- we need some
    #       kind of evaluation stack that pushes function partials and does
    #       not evaluated them until it is time for execution ... and the
    #       top of this stack will be the first command that needs to be run

    def __init__(
        self,
        s: str,
        command_engine: CommandEngine,
        base_evaluation_context: EvaluationContext
    ) -> None:
        self._source_str: str = s
        self._command_engine = command_engine
        self._base_evaluation_context = base_evaluation_context
        self._evaluation_context_chain: List[EvaluationContext] = []
        self._warnings: List[ShlexerWarning] = []
        self._open_paren_pos_stack: List[int] = []

        # TODO: other attributes
        # TODO: what should be public?

        self._tokens: List[str] = []
        self._state: Shtate = Shtate.ENTER_NEW_CONTEXT
        self._pos: int = 0
        if s:
            self._parse()

    @property
    def state(
        self
    ) -> Shtate:
        """The current state of the parser."""
        return self._state

    @property
    def source_str(
        self
    ) -> str:
        """The original string that was parsed."""
        return self._source_str

    @property
    def command_engine(
        self
    ) -> CommandEngine:
        """The engine used to lookup commands, as parsed."""

    @property
    def warnings(
        self
    ) -> List[ShlexerWarning]:
        """Warnings that occurred during parsing."""
        return self._warnings

    @property
    def still_parsing(
        self
    ) -> bool:
        """Whether the initial parsing is still ongoing."""
        return self._pos < len(self._source_str)

    @property
    def _char(
        self
    ) -> str:
        """Character pointed to by :data:`_pos`."""
        return self._source_str[self._pos]

    @property
    def _curr_evaluation_context(
        self
    ) -> Optional[EvaluationContext]:
        """Get the current :class:`EvaluationContext`."""
        if self._evaluation_context_chain:
            return self._evaluation_context_chain[-1]

        return None

    def _add_evaluation_context(
        self
    ) -> None:
        """Add a new :class:`EvaluationContext` to the chain."""
        self._evaluation_context_chain.append(
            self._base_evaluation_context.clone())

    def _peek_next_token(
        self
    ) -> Optional[str]:
        """TODO."""
        # TODO
        pass

    def _chomp_next_token(
        self
    ) -> Optional[str]:
        """Find the next matching token, advancing the current position."""
        token = self._peek_next_token()
        if token is None:
            return None

        self._tokens.append(token)
        self._pos += len(token)
        return token

    def _parse(
        self
    ) -> None:
        """The core functionality of this class."""
        while self.still_parsing:
            start_pos: int = self._pos

            next_token: Optional[str] = self._chomp_next_token()
            if next_token is None:
                # TODO: what puts us in this position?
                pass
            elif self.state == Shtate.ENTER_NEW_CONTEXT:
                self._add_evaluation_context()
                if next_token == ShellTokens.PAREN_OPEN_TOKEN:
                    self._open_paren_pos_stack.append(start_pos)
                    self._state = Shtate.ENTER_NEW_CONTEXT
                elif next_token in ShellTokens.SYMBOL_TOKENS:
                    # TODO: how are we raising errors?
                    pass
                else:
                    # token should be a command
                    # TODO
                    pass
            elif self.state == Shtate.IN_COMMAND_BODY:
                # TODO
                pass
            else:
                raise ValueError(
                    'Encountered unknown state in Shlexer._parse!')
