"""Tests for the ``PagePath`` class."""

from typing import Tuple

import pytest

from almanac import PagePath, PositionalValueError


class TestPagePath:
    def assert_segments(self, path: str, expected: Tuple[str, ...]):
        assert PagePath(path).segments == expected

    def assert_parent_dirs(self, path: str, expected: Tuple[str, ...]):
        assert PagePath(path).parent_dirs == expected

    def assert_path(self, path: str, expected: str):
        assert PagePath(path).path == expected

    def test_non_absolute(self):
        with pytest.raises(PositionalValueError):
            PagePath("a/b/c")

    def test_slash_collapsing(self):
        self.assert_path("//a/b/c/", "/a/b/c")

        self.assert_path("////////a//a//a/a///////a/a/a/a//a/a", "/a/a/a/a/a/a/a/a/a/a")

        self.assert_path("//////////", "/")

        self.assert_path("/b///////", "/b")

        self.assert_path("/b////c/", "/b/c")

    def test_path_segments(self):
        self.assert_segments(
            "/a/b/c/d/e/f/g",
            (
                "/",
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
            ),
        )

        self.assert_segments(
            "/a--//-//b",
            (
                "/",
                "a--",
                "-",
                "b",
            ),
        )

        self.assert_segments(
            "/a/b/c/d/",
            (
                "/",
                "a",
                "b",
                "c",
                "d",
            ),
        )

        self.assert_segments("/", ("/",))

        self.assert_segments("/////", ("/",))

    def test_parent_directories(self):
        self.assert_parent_dirs("/", tuple())

        self.assert_parent_dirs("/a", ("/",))

        self.assert_parent_dirs(
            "/a/b/",
            (
                "/",
                "/a",
            ),
        )

        self.assert_parent_dirs(
            "/a/b/c/d/e",
            (
                "/",
                "/a",
                "/a/b",
                "/a/b/c",
                "/a/b/c/d",
            ),
        )
