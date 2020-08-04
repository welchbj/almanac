"""Tests for the ``PageNavigator`` class."""

from typing import List
from unittest import TestCase

from almanac import (
    BlockedPageOverwriteError,
    DirectoryPage,
    OutOfBoundsPageError,
    PageNavigator,
    PathSyntaxError
)


class PageNavigatorTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a populated PageNavigator."""
        cls.page_navigator = PageNavigator()
        paths = [
            '/',
            '/one',
            '/one/a',
            '/one/a/b',
            '/one/a/b/c',
            '/two',
            '/two/a',
            '/two/a/b',
            '/two/a/bb',
            '/two/a/b/c/dd',
            '/two/a/b/c/d/e',
            '/three/a/b/c/d/e/f/g',
            '/three/a/b/cc'
        ]
        for path in paths:
            cls.page_navigator[path] = DirectoryPage(path)

    def setUp(self):
        """Reset the PageNavigator to the root directory."""
        self.page_navigator.change_directory('/')

    def assert_exploded_path_equals(self, path_to_explode: str, expected: str):
        """Utility for testing exploded path handling."""
        self.assertEqual(
            self.page_navigator.explode(path_to_explode),
            expected
        )

    def assert_path_is(self, expected: str):
        """Assert the current path of the page_navigator."""
        self.assertEqual(
            str(self.page_navigator.current_page.path),
            expected
        )

    def assert_match_is(self, pattern: str, expected: List[str]):
        """Assert the matches to the pattern."""
        self.assertEqual(
            [m.path for m in self.page_navigator.match(pattern)],
            expected
        )

    def test_back_and_forward(self):
        self.assert_path_is('/')

        self.page_navigator.back()
        self.assert_path_is('/')
        self.page_navigator.forward()
        self.assert_path_is('/')

        self.page_navigator.change_directory('one')
        self.assert_path_is('/one')
        self.page_navigator.back()
        self.assert_path_is('/')
        self.page_navigator.forward()
        self.assert_path_is('/one')
        self.page_navigator.back()
        self.assert_path_is('/')

        self.page_navigator.change_directory('/one')
        self.page_navigator.change_directory('/one/a')
        self.assert_path_is('/one/a')
        self.page_navigator.back()
        self.assert_path_is('/one')
        self.page_navigator.back()
        self.assert_path_is('/')
        self.page_navigator.forward()
        self.assert_path_is('/one')
        self.page_navigator.forward()
        self.assert_path_is('/one/a')

        self.page_navigator.change_directory('/')
        self.page_navigator.back()
        self.assert_path_is('/one/a')
        self.page_navigator.back()
        self.assert_path_is('/one')

    def test_match(self):
        self.assert_match_is(
            '/*',
            [
                '/',
                '/one',
                '/one/a',
                '/one/a/b',
                '/one/a/b/c',
                '/three',
                '/three/a',
                '/three/a/b',
                '/three/a/b/c',
                '/three/a/b/c/d',
                '/three/a/b/c/d/e',
                '/three/a/b/c/d/e/f',
                '/three/a/b/c/d/e/f/g',
                '/three/a/b/cc',
                '/two',
                '/two/a',
                '/two/a/b',
                '/two/a/b/c',
                '/two/a/b/c/d',
                '/two/a/b/c/d/e',
                '/two/a/b/c/dd',
                '/two/a/bb',
            ])

        self.assert_match_is(
            '/one/?',
            [
                '/one/a',
            ])

        self.assert_match_is(
            '/one/*',
            [
                '/one/a',
                '/one/a/b',
                '/one/a/b/c',
            ])

        self.assert_match_is(
            '/three/a/*/c*',
            [
                '/three/a/b/c',
                '/three/a/b/c/d',
                '/three/a/b/c/d/e',
                '/three/a/b/c/d/e/f',
                '/three/a/b/c/d/e/f/g',
                '/three/a/b/cc',
            ])

    def test_magic_access_methods(self):
        # test adding a page
        p = PageNavigator()
        self.assertTrue('/' in p)

        dir_page_a = DirectoryPage('/a')
        p['/a/'] = dir_page_a
        self.assertTrue('/' in p)
        self.assertTrue('/a' in p)

        self.assertEqual(dir_page_a.parent, p['/'])
        self.assertTrue(dir_page_a in p['/'].children)

        # test intermediate directory creation
        p.add_directory_page('/a/b/c/d')
        p.add_directory_page('/aa/bb/cc')
        self.assertTrue('/' in p)
        self.assertTrue('/a' in p)
        self.assertTrue('/a/b' in p)
        self.assertTrue('/a/b/c' in p)
        self.assertTrue('/a/b/c/d' in p)
        self.assertTrue('/aa' in p)
        self.assertTrue('/aa/bb' in p)
        self.assertTrue('/aa/bb/cc' in p)

        self.assertEqual(p['/a/b/c/d'].parent, p['/a/b/c'])
        self.assertTrue(p['/a/b/c/d'] in p['/a/b/c'].children)
        self.assertEqual(p['/a/b/c'].parent, p['/a/b'])
        self.assertTrue(p['/a/b/c'] in p['/a/b'].children)
        self.assertEqual(p['/a/b'].parent, p['/a'])

        self.assertTrue(p['/a/b'] in p['/a'].children)
        self.assertEqual(p['/a'].parent, p['/'])
        self.assertTrue(p['/a'] in p['/'].children)

        p.add_directory_page('/a/bb/c')
        self.assertEqual(p['/a/bb'].parent, p['/a'])
        self.assertEqual(p['/a/bb/c'].parent, p['/a/bb'])
        self.assertEqual(p['/a/b'].parent, p['/a'])

        self.assertTrue(p['/a/bb'] in p['/a'].children)
        self.assertTrue(p['/a/b'] in p['/a'].children)

        # test overwriting existing pages
        p['/a/b'] = DirectoryPage('/a/b')
        self.assertEqual(p['/a/b'].parent, p['/a'])
        self.assertTrue(p['/a/b'] in p['/a'].children)

        p['/'] = DirectoryPage('/')
        self.assertEqual(p['/a'].parent, p['/'])
        self.assertTrue(p['/a'] in p['/'].children)
        self.assertEqual(p['/aa'].parent, p['/'])
        self.assertTrue(p['/aa'] in p['/'].children)

        with self.assertRaises(BlockedPageOverwriteError) as cm:
            p.add_directory_page('/')
        self.assertEqual(cm.exception.path, '/')

        with self.assertRaises(BlockedPageOverwriteError) as cm:
            p.add_directory_page('/a/b/c/d')
        self.assertEqual(cm.exception.path, '/a/b/c/d')

        # test deleting pages
        del p['/a']
        del p['/aa']
        self.assertEqual(len(p), 1)

        # TODO: check on p['/'].children

    def test_explode_empty_path(self):
        """Test proper handling of an empty path."""
        self.assert_exploded_path_equals('', '/')

        self.page_navigator.change_directory('one')
        self.assert_exploded_path_equals('', '/one')

        self.page_navigator.change_directory('a')
        self.assert_exploded_path_equals('', '/one/a')

        self.page_navigator.change_directory('./b')
        self.assert_exploded_path_equals('', '/one/a/b')

        self.page_navigator.change_directory('.')
        self.assert_exploded_path_equals('', '/one/a/b')

        self.page_navigator.change_directory('c')
        self.assert_exploded_path_equals('', '/one/a/b/c')

        self.page_navigator.change_directory('..')
        self.assert_exploded_path_equals('', '/one/a/b')

        self.page_navigator.change_directory('.././')
        self.assert_exploded_path_equals('', '/one/a')

        self.page_navigator.change_directory('../../two/.')
        self.assert_exploded_path_equals('', '/two')

        self.page_navigator.change_directory('../././././.')
        self.assert_exploded_path_equals('', '/')

        self.page_navigator.change_directory('./one/../two/a/bb')
        self.assert_exploded_path_equals('', '/two/a/bb')

    def test_explode_single_dots(self):
        """Test proper handling of single dots in paths."""
        self.assert_exploded_path_equals('.', '/')
        self.assert_exploded_path_equals('./.', '/')
        self.assert_exploded_path_equals('././', '/')
        self.assert_exploded_path_equals('././/', '/')
        self.assert_exploded_path_equals('.//.//', '/')
        self.assert_exploded_path_equals('./././././.', '/')
        self.assert_exploded_path_equals('././././', '/')

        self.assert_exploded_path_equals('one/.', '/one')
        self.assert_exploded_path_equals('one/./', '/one')
        self.assert_exploded_path_equals('one/.//', '/one')
        self.assert_exploded_path_equals('./one', '/one')
        self.assert_exploded_path_equals('./one/', '/one')
        self.assert_exploded_path_equals('./one//', '/one')
        self.assert_exploded_path_equals('./one///', '/one')
        self.assert_exploded_path_equals('./one////', '/one')
        self.assert_exploded_path_equals('./one/.', '/one')
        self.assert_exploded_path_equals('./one//.', '/one')
        self.assert_exploded_path_equals('./one///.', '/one')
        self.assert_exploded_path_equals('./one////.', '/one')
        self.assert_exploded_path_equals('./././one', '/one')
        self.assert_exploded_path_equals('/./one', '/one')
        self.assert_exploded_path_equals('/./././one', '/one')

        self.page_navigator.change_directory('one/a')
        self.assert_exploded_path_equals('.', '/one/a')
        self.assert_exploded_path_equals('./', '/one/a')
        self.assert_exploded_path_equals('././', '/one/a')

    def test_explode_mixed_dots(self):
        """Test a mix of single and double dot operators in paths."""
        self.assert_exploded_path_equals('', '/')
        self.assert_exploded_path_equals('.', '/')

        self.page_navigator.change_directory('two')
        self.page_navigator.change_directory('a')
        self.assert_exploded_path_equals('.', '/two/a')
        self.assert_exploded_path_equals('..', '/two')
        self.assert_exploded_path_equals('../', '/two')
        self.assert_exploded_path_equals('../.', '/two')
        self.assert_exploded_path_equals('.././', '/two')
        self.assert_exploded_path_equals('.././', '/two')
        self.assert_exploded_path_equals('../..', '/')
        self.assert_exploded_path_equals('../../', '/')
        self.assert_exploded_path_equals('../../.', '/')
        self.assert_exploded_path_equals('../.././', '/')

        self.page_navigator.change_directory('/three/a/b/cc')
        self.assert_exploded_path_equals('.', '/three/a/b/cc')
        self.assert_exploded_path_equals('..', '/three/a/b')
        self.assert_exploded_path_equals('../', '/three/a/b')
        self.assert_exploded_path_equals('../.', '/three/a/b')
        self.assert_exploded_path_equals('.././..', '/three/a')
        self.assert_exploded_path_equals('.././../', '/three/a')
        self.assert_exploded_path_equals('.././../.', '/three/a')
        self.assert_exploded_path_equals('.././.././', '/three/a')
        self.assert_exploded_path_equals('../../../..', '/')
        self.assert_exploded_path_equals('../../../../', '/')
        self.assert_exploded_path_equals('../../../../.', '/')
        self.assert_exploded_path_equals('../../.././././././././..', '/')
        self.assert_exploded_path_equals('../../.././././././././../', '/')

        # test some absolute paths
        self.assert_exploded_path_equals('/////////.', '/')
        self.assert_exploded_path_equals('/././././//////././//././/./', '/')
        self.assert_exploded_path_equals('/one/../', '/')
        self.assert_exploded_path_equals('/./one/../one', '/one')
        self.assert_exploded_path_equals('/one/a/b/../.././////', '/one')

    def test_explode_invalid_interjected_dots(self):
        """Test invalid placement of the dot operator."""
        with self.assertRaises(PathSyntaxError) as cm:
            self.page_navigator.change_directory('/snippets/.segment')
        self.assertEqual(cm.exception.error_pos, 10)

        with self.assertRaises(PathSyntaxError) as cm:
            self.page_navigator.change_directory('/..segment')
        self.assertEqual(cm.exception.error_pos, 3)

        with self.assertRaises(PathSyntaxError) as cm:
            self.page_navigator.change_directory('/./seg.ment')
        self.assertEqual(cm.exception.error_pos, 6)

        with self.assertRaises(PathSyntaxError) as cm:
            self.page_navigator.change_directory('/segment.')
        self.assertEqual(cm.exception.error_pos, 8)

        with self.assertRaises(PathSyntaxError) as cm:
            self.page_navigator.change_directory('/segment/another_segment..')
        self.assertEqual(cm.exception.error_pos, 24)

    def test_explode_invalid_parent_references(self):
        """Test references to parent directories outside of the application."""
        with self.assertRaises(OutOfBoundsPageError) as cm:
            self.page_navigator.change_directory('..')
        self.assertEqual(cm.exception.path, '..')

        self.page_navigator.change_directory('one')
        with self.assertRaises(OutOfBoundsPageError) as cm:
            self.page_navigator.change_directory('../..')
        self.assertEqual(cm.exception.path, '../..')

        self.page_navigator.change_directory('a')
        with self.assertRaises(OutOfBoundsPageError) as cm:
            self.page_navigator.change_directory('../../..')
        self.assertEqual(cm.exception.path, '../../..')

        self.page_navigator.change_directory('b')
        with self.assertRaises(OutOfBoundsPageError) as cm:
            self.page_navigator.change_directory('../../../../segment')
        self.assertEqual(cm.exception.path, '../../../../segment')
