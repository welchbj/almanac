"""Implementation of the ``DirectoryPage`` class."""

from typing import (
    Tuple)

from .abstract_page import (
    AbstractPage)


class DirectoryPage(AbstractPage):
    """A page that holds references to other pages.

    TODO

    """

    @property
    def help_text(
        self
    ) -> str:
        return (
            'TODO: DirectoryPage help_text')

    @property
    def info_text(
        self
    ) -> str:
        return (
            'TODO: DirectoryPage info_text')

    def get_prompt(
        self
    ) -> str:
        return f'directory [{self._path}]> '
