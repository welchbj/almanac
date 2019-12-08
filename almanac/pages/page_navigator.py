"""Implementation of the ``PageNavigator`` class."""

from enum import (
    auto,
    Enum)
from fnmatch import (
    filter as fn_filter)
from itertools import (
    chain)
from typing import (
    Iterable,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Type)

from .abstract_page import (
    AbstractPage)
from .directory_page import (
    DirectoryPage)
from .page_path import (
    PagePath,
    PagePathLike)
from ..errors import (
    PositionalValueError)
from ..utils import (
    pairwise)


class _PathExplodeState(Enum):
    BEGIN = auto()
    IN_SEGMENT = auto()
    ATE_SLASH = auto()
    ATE_ONE_DOT = auto()
    ATE_TWO_DOTS = auto()


class PageNavigator(MutableMapping[PagePathLike, AbstractPage]):
    """Encapsulation of page navigation and history logic."""

    def __init__(
        self,
        directory_page_cls: Type[DirectoryPage] = DirectoryPage
    ) -> None:
        self._directory_page_cls = directory_page_cls
        self._root_page: AbstractPage = self._directory_page_cls('/')
        self._current_page: AbstractPage = self._root_page
        self._page_table: MutableMapping[PagePath, AbstractPage] = {}

        self._back_page_history_stack: List[AbstractPage] = []
        self._forward_page_history_stack: List[AbstractPage] = []

        self['/'] = self._root_page

    def change_directory(
        self,
        destination: PagePathLike
    ) -> None:
        """Change the current directory of this navigator.

        Args:
            destination: The page to change to, which will be exploded into
                an absolute path.

        Raises:
            PositionalValueError: If a synactical error occured during the
                path parsing.
            ValueError: If the specified destination is invalid or does not
                exist.

        """
        full_path: str = self.explode(destination)
        if full_path not in self:
            raise ValueError(f'Exploded path {str(full_path)} not present in '
                             'this navigator')
        elif full_path == self.current_page.path:
            return

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
    ) -> Iterable[AbstractPage]:
        """Match stored pages against ``fnmatch`` patterns."""
        paths: List[str] = [page.path for page in self._page_table.keys()]
        for match in sorted(fn_filter(paths, pattern)):
            yield self[match]

    def explode(
        self,
        path: PagePathLike
    ) -> str:
        """Parse a user-specified path into an existing page.

        TODO: example

        Args:
            path: The path to explode (i.e., expand ``.`` and ``..``) into an
                absolute path.

        Returns:
            The exploded absolute path. This value is not guaranteed to exist
            within this :class:`PageNavigator`.

        Raises:
            ValueError: If a malformed path is received or invalid parent
                directories are referenced via the ``..`` operator.
            PositionalValueError: If an invalid character sequence is
                encountered, such as dots in the middle of of a path segment.

        """
        path = str(path)

        if not path:
            return str(self._current_page.path)

        if path == '/':
            # guaranteed to exist, so we can short-circuit this
            return '/'
        elif path.startswith('/'):
            exploded_path = ''
        else:
            exploded_path = str(self._current_page.path)
            if exploded_path[-1] != '/':
                exploded_path += '/'

        state = _PathExplodeState.BEGIN

        for i, c in enumerate(chain(path, (None,))):
            if state == _PathExplodeState.BEGIN:
                if c == '/':
                    state = _PathExplodeState.ATE_SLASH
                elif c == '.':
                    state = _PathExplodeState.ATE_ONE_DOT
                elif c is None:
                    # this shouldn't be possible
                    pass
                else:
                    exploded_path += c
            elif state == _PathExplodeState.IN_SEGMENT:
                if c == '/':
                    state = _PathExplodeState.ATE_SLASH
                elif c == '.':
                    raise PositionalValueError(
                        'Invalid dot position in path', i)
                elif c is None:
                    pass
                else:
                    exploded_path += c
            elif state == _PathExplodeState.ATE_SLASH:
                if c == '/':
                    pass
                elif c == '.':
                    state = _PathExplodeState.ATE_ONE_DOT
                elif c is None:
                    pass
                else:
                    if not exploded_path or exploded_path[-1] != '/':
                        exploded_path += '/'
                    exploded_path += c
                    state = _PathExplodeState.IN_SEGMENT
            elif state == _PathExplodeState.ATE_ONE_DOT:
                if c == '/':
                    state = _PathExplodeState.ATE_SLASH
                elif c == '.':
                    state = _PathExplodeState.ATE_TWO_DOTS
                elif c is None:
                    pass
                else:
                    raise PositionalValueError(
                        'Invalid dot position in path', i - 1)
            elif state == _PathExplodeState.ATE_TWO_DOTS:
                if c == '/' or c is None:
                    exploded_path = PagePath.un_trailing_slashify(
                        exploded_path)
                    if exploded_path not in self:
                        raise ValueError(
                            'Attempted to reference non-existent directory')

                    referenced_page = self[exploded_path]
                    if referenced_page.parent is None:
                        raise ValueError(
                            'Attempted to reference parent directory beyond '
                            'application scope')

                    exploded_path = str(referenced_page.parent.path)
                    state = _PathExplodeState.ATE_SLASH
                elif c == '.':
                    raise PositionalValueError(
                        'You can\'t have three dots in a row!', i)
                else:
                    raise PositionalValueError('Expected a slash!', i)

        if not exploded_path:
            exploded_path = '/'

        return PagePath.un_trailing_slashify(exploded_path)

    @property
    def directory_page_cls(
        self
    ) -> Type[DirectoryPage]:
        """The class used to create new directory pages."""
        return self._directory_page_cls

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
    ) -> Iterator[PagePathLike]:
        for path in self._page_table.keys():
            yield path

    def __len__(
        self
    ) -> int:
        return len(self._page_table.keys())

    def set_page(
        self,
        key: PagePathLike,
        value: AbstractPage,
        allow_overwrite: bool = True
    ) -> None:
        path = PagePath(self.explode(key))
        if path not in self:
            self._page_table[path] = value

            path_str_iter = chain(path.parent_dirs, (str(path),))
            dir_pairs = list(pairwise(path_str_iter))
            for (parent, child) in reversed(dir_pairs):
                child_page: Optional[AbstractPage] = self.get(child, None)
                if child_page is None:
                    child_page = self.directory_page_cls(child)
                    self._page_table[PagePath(child)] = child_page

                parent_page: Optional[AbstractPage] = self.get(parent, None)
                if parent_page is None:
                    parent_page = self.directory_page_cls(parent)
                    self._page_table[PagePath(parent)] = parent_page

                parent_page.children.add(child_page)
                child_page.parent = parent_page
        elif not allow_overwrite:
            raise ValueError(
                f'Attempted to overwrite page at {path} with'
                'allow_overwrite kwarg set to False')
        else:
            # overwriting an existing page
            old_page = self[path]
            new_page = value
            new_page.children.update(old_page.children)
            new_page.parent = old_page.parent
            self._page_table[path] = new_page

    def __setitem__(
        self,
        key: PagePathLike,
        value: AbstractPage
    ) -> None:
        self.set_page(key, value, allow_overwrite=True)

    def add_directory_page(
        self,
        path: PagePathLike
    ) -> DirectoryPage:
        """Add a directory page at the specified path.

        This method is only used for adding pages that do not already exist. It
        will also create any intermediate directories within the path that do
        not already exist.

        Returns:
            The created :class:`DirectoryPage`.

        Raises:
            ValueError: If an existing page would be overwritten by the
                operation.

        .. code-block:: python

            >>> from almanac import PageNavigator
            >>> p = PageNavigator()
            >>> p.add_directory_page('/a_page')
            <DirectoryPage [/a_page]>
            >>> print(p)
            /
            /a_page
            >>> p.add_directory_page('/a_page/and/some/others')
            <DirectoryPage [/a_page/and/some/others]>
            >>> print(p)
            /
            /a_page
            /a_page/and
            /a_page/and/some
            /a_page/and/some/others

        """
        dir_page = self.directory_page_cls(path)
        self.set_page(
            PagePath(path),
            dir_page,
            allow_overwrite=False)
        return dir_page

    def __delitem__(
        self,
        key: PagePathLike
    ) -> None:
        PagePath.assert_absolute_path(key)

        page_path = PagePath(key)
        if page_path not in self:
            raise KeyError(
                f'Path {page_path} does not exist in this navigator')

        # delete all children of the specified path
        for child in self.match(page_path.path + '/*'):
            child_path: PagePath = child.path
            child_page = self._page_table[child_path]

            child_page.parent = None
            child_page.children.clear()

            del self._page_table[child_path]

        existing_page = self._page_table[page_path]

        existing_page.parent.children.remove(existing_page)  # type: ignore
        del self._page_table[page_path]

    def __getitem__(
        self,
        key: PagePathLike
    ) -> AbstractPage:
        try:
            path = PagePath(self.explode(key))
            return self._page_table[path]
        except KeyError as e:
            raise KeyError(f'Path {str(key)} does not exist!') from e

    def __str__(
        self
    ) -> str:
        return '\n'.join(str(page.path) for page in self.match('*'))

    def __repr__(
        self
    ) -> str:
        return f'<{self.__class__.__qualname__} [{len(self)} pages]>'
