"""Common dev tasks for the ``almanac`` project."""

import os
import subprocess
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from contextlib import contextmanager

from livereload import Server

HERE = os.path.dirname(os.path.abspath(__file__))
README_FILE = os.path.join(HERE, 'README.md')
DOCS_DIR = os.path.join(HERE, 'docs')
ALMANAC_DIR = os.path.join(HERE, 'almanac')
TESTS_DIR = os.path.join(ALMANAC_DIR, 'tests')


class TestFailureError(Exception):
    """An exception type for failed tests."""


class SubprocessFailureError(Exception):
    """An exception type for a subprocess exiting with a non-zero exit code."""


@contextmanager
def _cwd(new_cwd):
    """Context manager for temporarily changing the cwd."""
    old_cwd = os.getcwd()
    os.chdir(new_cwd)
    yield
    os.chdir(old_cwd)


def build_docs():
    """Build the HTML documentation site."""
    with _cwd(DOCS_DIR):
        exit_code = subprocess.call('make html', shell=True)

    if exit_code:
        print('Something went wrong building the docs', file=sys.stderr)
        raise SubprocessFailureError


def serve_docs(port: int = 8888):
    """Serve the documentation site on a local livereload server."""
    build_docs()

    server = Server()

    watch_patterns = [
        'docs/*.rst',
        'docs/**/*.rst',
        'docs/*.py',
        'almanac/**/*.py'
    ]
    for pattern in watch_patterns:
        server.watch(pattern, build_docs)

    server.serve(root=f'{DOCS_DIR}/_build/html', host='127.0.0.1', port=port)


TASKS = {
    'build-docs': build_docs,
    'serve-docs': serve_docs
}


def get_parsed_args():
    """Get the parsed command line arguments."""
    parser = ArgumentParser(
        prog='tasks.py',
        description='Helper script for running almanac project tasks',
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        'task',
        action='store',
        metavar='TASK',
        type=str,
        choices=sorted(TASKS.keys()),
        help='the task to run'
    )

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
