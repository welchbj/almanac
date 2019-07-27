"""Tests for the ``PagePath`` class."""

from typing import (
    Tuple)
from unittest import (
    TestCase)

from almanac import (
    PagePath,
    PositionalValueError)


class PagePathTestCase(TestCase):

    def assert_segments(self, path: str, expected: Tuple[str, ...]):
        self.assertEqual(
            PagePath(path).segments,
            expected)

    def assert_parent_dirs(self, path: str, expected: Tuple[str, ...]):
        self.assertEqual(
            PagePath(path).parent_dirs,
            expected)

    def assert_path(self, path: str, expected: str):
        self.assertEqual(
            PagePath(path).path,
            expected)

    def test_non_absolute(self):
        with self.assertRaises(PositionalValueError):
            PagePath('a/b/c')

    def test_slash_collapsing(self):
        self.assert_path(
            '//a/b/c/',
            '/a/b/c')

        self.assert_path(
            '////////a//a//a/a///////a/a/a/a//a/a',
            '/a/a/a/a/a/a/a/a/a/a')

        self.assert_path(
            '//////////',
            '/')

        self.assert_path(
            '/b///////',
            '/b')

        self.assert_path(
            '/b////c/',
            '/b/c')

    def test_path_segments(self):
        self.assert_segments(
            '/a/b/c/d/e/f/g',
            ('a', 'b', 'c', 'd', 'e', 'f', 'g',))

        self.assert_segments(
            '/a--//-//b',
            ('a--', '-', 'b',))

        self.assert_segments(
            '/a/b/c/d/',
            ('a', 'b', 'c', 'd',))

        self.assert_segments(
            '/',
            tuple())

        self.assert_segments(
            '/////',
            tuple())

    def test_parent_directories(self):
        self.assert_parent_dirs(
            '/',
            tuple())

        self.assert_parent_dirs(
            '/a',
            ('/',))

        self.assert_parent_dirs(
            '/a/b/',
            ('/', '/a',))

        self.assert_parent_dirs(
            '/a/b/c/d/e',
            (
                '/',
                '/a',
                '/a/b',
                '/a/b/c',
                '/a/b/c/d',
            ))

    def test_invalid_characters(self):
        invalid_paths = (
            '/1/2/3 ',
            ' /1/2/3',
            '/ 1/2/3',
            './a/b',
            '/.a/b',
            '/a/.b',
            '/a/b.',
            '/a/b./',
            '/a/b/.',
            '/a---b/!',
            '/a_@b/',)

        for path in invalid_paths:
            with self.assertRaises(PositionalValueError):
                PagePath(path)
