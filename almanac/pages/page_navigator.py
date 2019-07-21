"""Implementation of the ``PageNavigator`` class."""

from collections import (
    MutableMapping as cMutableMapping)
from fnmatch import (
    filter as fn_filter)
from functools import (
    partial)
from itertools import (
    chain)
from typing import (
    Iterator,
    List,
    MutableMapping as tMutableMapping,
    Tuple)

from .abstract_page import (
    AbstractPage)
from .directory_page import (
    DirectoryPage)
from .page_path import (
    PagePath,
    PagePathLike)

PageMutableMapping = tMutableMapping[PagePathLike, AbstractPage]


class PageNavigator(cMutableMapping, PageMutableMapping):
    """Encapsulation of page navigation and history logic."""

    def __init__(
        self
    ) -> None:
        self._root_page: AbstractPage = DirectoryPage('/')
        self._current_page: AbstractPage = self._root_page
        self._page_table: tMutableMapping[PagePath, AbstractPage] = {}

        self._back_page_history_stack: List[AbstractPage] = []
        self._forward_page_history_stack: List[AbstractPage] = []

        self['/'] = self._root_page

    def change_directory(
        self,
        destination: PagePathLike
    ) -> None:
        """Change the current directory of this navigator.

        Raises:
            ValueError: If the specified destination is either unreachable or
                does not exist.

        """
        full_path: PagePath = self._current_page.explode(destination)
        if full_path not in self:
            raise ValueError(f'Exploded path {str(full_path)} not present in '
                             'this navigator')

        self._back_page_history_stack.append(self._current_page)
        self._current_page = self[full_path]

    def forward(
        self
    ) -> None:
        """Move forward in the page history."""
        if not self._forward_page_history_stack:
            # do nothing if there is no forward page history
            return

        self._back_page_history_stack.append(self._current_page)
        self._current_page = self._forward_page_history_stack.pop()

    def back(
        self
    ) -> None:
        """Move backward in the page history."""
        if not self._back_page_history_stack:
            # do nothing if there is back page no history
            return

        self._forward_page_history_stack.append(self._current_page)
        self._current_page = self._back_page_history_stack.pop()

    def match(
        self,
        pattern: str
    ) -> Iterator[AbstractPage]:
        """Match stored pages against ``fnmatch`` patterns."""
        paths: List[str] = [page.path for page in self._page_table.keys()]
        for match in fn_filter(paths, pattern):
            yield match

    @property
    def root_page(
        self
    ) -> AbstractPage:
        """The root page within this navigator."""
        return self._root_page

    @property
    def current_page(
        self
    ) -> AbstractPage:
        """The current page within this navigator."""
        return self._current_page

    def __iter__(
        self
    ) -> Tuple[PagePath, AbstractPage]:
        for path, page in self._page_table.mapping():
            yield (path, page,)

    def __len__(
        self
    ) -> int:
        return len(self._page_table.keys())

    def __setitem__(
        self,
        key: PagePathLike,
        value: AbstractPage,
        allow_overwrite: bool = True
    ) -> None:
        path = PagePath(key)
        if path not in self:
            self._page_table[path] = value
        elif not allow_overwrite:
            raise ValueError(
                f'Attempted to overwrite page at {path}')
        else:
            # overwriting an existing page
            old_page = self[path]
            new_page = value
            new_page.children.extend(old_page.children)
            new_page.parent = old_page.parent
            self[path] = new_page

    add_page = partial(__setitem__, allow_overwrite=False)

    def __delitem__(
        self,
        key: PagePathLike
    ) -> None:
        page_path = PagePath(key)
        if page_path not in self:
            raise KeyError(
                f'Path {page_path} does not exist in this navigator')

        # delete the specified path and all children
        children_iter = chain(
            self.match(page_path.path + '/*'),
            self.match(page_path.path + '/**/*'))
        for child in children_iter:
            del self._page_table[child.path]

        del self._page_table[page_path.path]

    def __getitem__(
        self,
        key: PagePathLike
    ) -> AbstractPage:
        try:
            path = PagePath(key)
            return self._page_table[path]
        except KeyError as e:
            raise KeyError(f'Path {str(key)} does not exist!') from e
