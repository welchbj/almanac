"""Common dev tasks for the ``almanac`` project."""

import doctest
import os
import unittest
import sys

import almanac

from argparse import (
    ArgumentParser,
    RawTextHelpFormatter)
from contextlib import (
    contextmanager)
from typing import (
    Any,
    Dict)


HERE = os.path.dirname(os.path.abspath(__file__))
README_FILE = os.path.join(HERE, 'README.md')
ALMANAC_DIR = os.path.join(HERE, 'almanac')
TESTS_DIR = os.path.join(ALMANAC_DIR, 'tests')


class TestFailureError(Exception):
    """An exception type for failed tests."""


@contextmanager
def _cwd(new_cwd):
    """Context manager for temporarily changing the cwd."""
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    yield
    os.chdir(old_cwd)


def test() -> None:
    """Run all unit and doc tests."""
    suite = unittest.defaultTestLoader.discover(
        TESTS_DIR,
        pattern='test_*.py',
        top_level_dir=HERE)

    doctest_modules = [
        almanac.core.application,
        almanac.core.shortcuts,

        # TODO: almanac.commands
        # TODO: almanac.errors
        # TODO: almanac.formatting
        # TODO: almanac.loaders

        # TODO: almanac.pages.search

        almanac.pages.abstract_page_provider,
        almanac.pages.abstract_page_serializer_mixin,
        almanac.pages.abstract_page,
        almanac.pages.directory_page,
        almanac.pages.page_navigator,
        almanac.pages.page_path,

        almanac.utils.fuzzy_matcher,
        almanac.utils.iteration
    ]

    doctest_files = [
        README_FILE
    ]

    doctest_kwargs: Dict[str, Any] = dict(
        optionflags=doctest.IGNORE_EXCEPTION_DETAIL)

    for module in doctest_modules:
        suite.addTests(
            doctest.DocTestSuite(
                module,
                **doctest_kwargs))

    for _file in doctest_files:
        suite.addTests(
            doctest.DocFileSuite(
                _file,
                module_relative=False,
                **doctest_kwargs))

    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise TestFailureError


TASKS = {
    'test': test
}


def get_parsed_args():
    """Get the parsed command line arguments."""
    parser = ArgumentParser(
        prog='tasks.py',
        description='Helper script for running almanac project tasks',
        formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        'task',
        action='store',
        metavar='TASK',
        type=str,
        choices=sorted(TASKS.keys()),
        help='the ttask to run')

    return parser.parse_args()


def main():
    """Main routine for running this script."""
    try:
        opts = get_parsed_args()
        task = TASKS[opts.task]
        task()
        return 0
    except TestFailureError:
        return 1
    except Exception as e:
        print('Received unexpected exception; re-raising it.', file=sys.stderr)
        raise e


if __name__ == '__main__':
    sys.exit(main())
