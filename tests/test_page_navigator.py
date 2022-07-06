"""Tests for the ``PageNavigator`` class."""

import pytest

from typing import List

from almanac import (
    BlockedPageOverwriteError,
    DirectoryPage,
    OutOfBoundsPageError,
    PageNavigator,
)


class TestPageNavigator:
    @classmethod
    def setup_class(cls):
        """Create a populated PageNavigator."""
        cls.page_navigator = PageNavigator()
        paths = [
            "/",
            "/one",
            "/one/a",
            "/one/a/b",
            "/one/a/b/c",
            "/two",
            "/two/a",
            "/two/a/b",
            "/two/a/bb",
            "/two/a/b/c/dd",
            "/two/a/b/c/d/e",
            "/three/a/b/c/d/e/f/g",
            "/three/a/b/cc",
        ]
        for path in paths:
            cls.page_navigator[path] = DirectoryPage(path)

    def setup_method(self):
        """Reset the PageNavigator to the root directory."""
        self.page_navigator.change_directory("/")

    def assert_exploded_path_equals(self, path_to_explode: str, expected: str):
        """Utility for testing exploded path handling."""
        assert self.page_navigator.explode(path_to_explode) == expected  # type: ignore

    def assert_path_is(self, expected: str):
        """Assert the current path of the page_navigator."""
        assert str(self.page_navigator.current_page.path) == expected  # type: ignore

    def assert_match_is(self, pattern: str, expected: List[str]):
        """Assert the matches to the pattern."""
        assert [
            m.path for m in self.page_navigator.match(pattern)  # type: ignore
        ] == expected

    def test_back_and_forward(self):
        self.assert_path_is("/")

        self.page_navigator.back()
        self.assert_path_is("/")
        self.page_navigator.forward()
        self.assert_path_is("/")

        self.page_navigator.change_directory("one")
        self.assert_path_is("/one")
        self.page_navigator.back()
        self.assert_path_is("/")
        self.page_navigator.forward()
        self.assert_path_is("/one")
        self.page_navigator.back()
        self.assert_path_is("/")

        self.page_navigator.change_directory("/one")
        self.page_navigator.change_directory("/one/a")
        self.assert_path_is("/one/a")
        self.page_navigator.back()
        self.assert_path_is("/one")
        self.page_navigator.back()
        self.assert_path_is("/")
        self.page_navigator.forward()
        self.assert_path_is("/one")
        self.page_navigator.forward()
        self.assert_path_is("/one/a")

        self.page_navigator.change_directory("/")
        self.page_navigator.back()
        self.assert_path_is("/one/a")
        self.page_navigator.back()
        self.assert_path_is("/one")

    def test_match(self):
        self.assert_match_is(
            "/*",
            [
                "/",
                "/one",
                "/one/a",
                "/one/a/b",
                "/one/a/b/c",
                "/three",
                "/three/a",
                "/three/a/b",
                "/three/a/b/c",
                "/three/a/b/c/d",
                "/three/a/b/c/d/e",
                "/three/a/b/c/d/e/f",
                "/three/a/b/c/d/e/f/g",
                "/three/a/b/cc",
                "/two",
                "/two/a",
                "/two/a/b",
                "/two/a/b/c",
                "/two/a/b/c/d",
                "/two/a/b/c/d/e",
                "/two/a/b/c/dd",
                "/two/a/bb",
            ],
        )

        self.assert_match_is(
            "/one/?",
            [
                "/one/a",
            ],
        )

        self.assert_match_is(
            "/one/*",
            [
                "/one/a",
                "/one/a/b",
                "/one/a/b/c",
            ],
        )

        self.assert_match_is(
            "/three/a/*/c*",
            [
                "/three/a/b/c",
                "/three/a/b/c/d",
                "/three/a/b/c/d/e",
                "/three/a/b/c/d/e/f",
                "/three/a/b/c/d/e/f/g",
                "/three/a/b/cc",
            ],
        )

    def test_magic_access_methods(self):
        # test adding a page
        p = PageNavigator()
        assert "/" in p

        dir_page_a = DirectoryPage("/a")
        p["/a/"] = dir_page_a
        assert "/" in p
        assert "/a" in p

        assert dir_page_a.parent == p["/"]
        assert dir_page_a in p["/"].children

        # test intermediate directory creation
        p.add_directory_page("/a/b/c/d")
        p.add_directory_page("/aa/bb/cc")
        assert "/" in p
        assert "/a" in p
        assert "/a/b" in p
        assert "/a/b/c" in p
        assert "/a/b/c/d" in p
        assert "/aa" in p
        assert "/aa/bb" in p
        assert "/aa/bb/cc" in p

        assert p["/a/b/c/d"].parent == p["/a/b/c"]
        assert p["/a/b/c/d"] in p["/a/b/c"].children
        assert p["/a/b/c"].parent == p["/a/b"]
        assert p["/a/b/c"] in p["/a/b"].children
        assert p["/a/b"].parent == p["/a"]

        assert p["/a/b"] in p["/a"].children
        assert p["/a"].parent == p["/"]
        assert p["/a"] in p["/"].children

        p.add_directory_page("/a/bb/c")
        assert p["/a/bb"].parent == p["/a"]
        assert p["/a/bb/c"].parent == p["/a/bb"]
        assert p["/a/b"].parent == p["/a"]

        assert p["/a/bb"] in p["/a"].children
        assert p["/a/b"] in p["/a"].children

        # test overwriting existing pages
        p["/a/b"] = DirectoryPage("/a/b")
        assert p["/a/b"].parent == p["/a"]
        assert p["/a/b"] in p["/a"].children

        p["/"] = DirectoryPage("/")
        assert p["/a"].parent == p["/"]
        assert p["/a"] in p["/"].children
        assert p["/aa"].parent == p["/"]
        assert p["/aa"] in p["/"].children

        with pytest.raises(BlockedPageOverwriteError) as ctx:
            p.add_directory_page("/")
        assert ctx.value.path == "/"

        with pytest.raises(BlockedPageOverwriteError) as ctx:
            p.add_directory_page("/a/b/c/d")
        assert ctx.value.path == "/a/b/c/d"

        # test deleting pages
        del p["/a"]
        del p["/aa"]
        assert len(p) == 1

        # TODO: check on p['/'].children

    def test_explode_empty_path(self):
        """Test proper handling of an empty path."""
        self.assert_exploded_path_equals("", "/")

        self.page_navigator.change_directory("one")
        self.assert_exploded_path_equals("", "/one")

        self.page_navigator.change_directory("a")
        self.assert_exploded_path_equals("", "/one/a")

        self.page_navigator.change_directory("./b")
        self.assert_exploded_path_equals("", "/one/a/b")

        self.page_navigator.change_directory(".")
        self.assert_exploded_path_equals("", "/one/a/b")

        self.page_navigator.change_directory("c")
        self.assert_exploded_path_equals("", "/one/a/b/c")

        self.page_navigator.change_directory("..")
        self.assert_exploded_path_equals("", "/one/a/b")

        self.page_navigator.change_directory(".././")
        self.assert_exploded_path_equals("", "/one/a")

        self.page_navigator.change_directory("../../two/.")
        self.assert_exploded_path_equals("", "/two")

        self.page_navigator.change_directory("../././././.")
        self.assert_exploded_path_equals("", "/")

        self.page_navigator.change_directory("./one/../two/a/bb")
        self.assert_exploded_path_equals("", "/two/a/bb")

    def test_explode_single_dots(self):
        """Test proper handling of single dots in paths."""
        self.assert_exploded_path_equals(".", "/")
        self.assert_exploded_path_equals("./.", "/")
        self.assert_exploded_path_equals("././", "/")
        self.assert_exploded_path_equals("././/", "/")
        self.assert_exploded_path_equals(".//.//", "/")
        self.assert_exploded_path_equals("./././././.", "/")
        self.assert_exploded_path_equals("././././", "/")

        self.assert_exploded_path_equals("one/.", "/one")
        self.assert_exploded_path_equals("one/./", "/one")
        self.assert_exploded_path_equals("one/.//", "/one")
        self.assert_exploded_path_equals("./one", "/one")
        self.assert_exploded_path_equals("./one/", "/one")
        self.assert_exploded_path_equals("./one//", "/one")
        self.assert_exploded_path_equals("./one///", "/one")
        self.assert_exploded_path_equals("./one////", "/one")
        self.assert_exploded_path_equals("./one/.", "/one")
        self.assert_exploded_path_equals("./one//.", "/one")
        self.assert_exploded_path_equals("./one///.", "/one")
        self.assert_exploded_path_equals("./one////.", "/one")
        self.assert_exploded_path_equals("./././one", "/one")
        self.assert_exploded_path_equals("/./one", "/one")
        self.assert_exploded_path_equals("/./././one", "/one")

        self.page_navigator.change_directory("one/a")
        self.assert_exploded_path_equals(".", "/one/a")
        self.assert_exploded_path_equals("./", "/one/a")
        self.assert_exploded_path_equals("././", "/one/a")

    def test_explode_mixed_dots(self):
        """Test a mix of single and double dot operators in paths."""
        self.assert_exploded_path_equals("", "/")
        self.assert_exploded_path_equals(".", "/")

        self.page_navigator.change_directory("two")
        self.page_navigator.change_directory("a")
        self.assert_exploded_path_equals(".", "/two/a")
        self.assert_exploded_path_equals("..", "/two")
        self.assert_exploded_path_equals("../", "/two")
        self.assert_exploded_path_equals("../.", "/two")
        self.assert_exploded_path_equals(".././", "/two")
        self.assert_exploded_path_equals(".././", "/two")
        self.assert_exploded_path_equals("../..", "/")
        self.assert_exploded_path_equals("../../", "/")
        self.assert_exploded_path_equals("../../.", "/")
        self.assert_exploded_path_equals("../.././", "/")

        self.page_navigator.change_directory("/three/a/b/cc")
        self.assert_exploded_path_equals(".", "/three/a/b/cc")
        self.assert_exploded_path_equals("..", "/three/a/b")
        self.assert_exploded_path_equals("../", "/three/a/b")
        self.assert_exploded_path_equals("../.", "/three/a/b")
        self.assert_exploded_path_equals(".././..", "/three/a")
        self.assert_exploded_path_equals(".././../", "/three/a")
        self.assert_exploded_path_equals(".././../.", "/three/a")
        self.assert_exploded_path_equals(".././.././", "/three/a")
        self.assert_exploded_path_equals("../../../..", "/")
        self.assert_exploded_path_equals("../../../../", "/")
        self.assert_exploded_path_equals("../../../../.", "/")
        self.assert_exploded_path_equals("../../.././././././././..", "/")
        self.assert_exploded_path_equals("../../.././././././././../", "/")

        # test some absolute paths
        self.assert_exploded_path_equals("/////////.", "/")
        self.assert_exploded_path_equals("/././././//////././//././/./", "/")
        self.assert_exploded_path_equals("/one/../", "/")
        self.assert_exploded_path_equals("/./one/../one", "/one")
        self.assert_exploded_path_equals("/one/a/b/../.././////", "/one")

    def test_explode_invalid_parent_references(self):
        """Test references to parent directories outside of the application."""
        with pytest.raises(OutOfBoundsPageError) as ctx:
            self.page_navigator.change_directory("..")
        ctx.value.path == ".."

        self.page_navigator.change_directory("one")
        with pytest.raises(OutOfBoundsPageError) as ctx:
            self.page_navigator.change_directory("../..")
        ctx.value.path == "../.."

        self.page_navigator.change_directory("a")
        with pytest.raises(OutOfBoundsPageError) as ctx:
            self.page_navigator.change_directory("../../..")
        ctx.value.path == "../../.."

        self.page_navigator.change_directory("b")
        with pytest.raises(OutOfBoundsPageError) as ctx:
            self.page_navigator.change_directory("../../../../segment")
        ctx.value.path == "../../../../segment"
