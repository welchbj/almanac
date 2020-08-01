from __future__ import print_function

import os
import sys

try:
    from setuptools import find_packages, setup
except ImportError:
    print('`setuptools` is required for installation.\n',
          'You can install it using pip.', file=sys.stderr)
    sys.exit(1)

here = os.path.abspath(os.path.dirname(__file__))
readme_file = os.path.join(here, 'README.md')
deps_dir = os.path.join(here, 'deps')
prod_requirements_file = os.path.join(deps_dir, 'requirements.txt')
almanac_dir = os.path.join(here, 'almanac')
version_file = os.path.join(almanac_dir, 'version.py')

pypi_name = 'almanac'
description = 'a framework for interactive, page-based console applications'
license = 'MIT'
author = 'Brian Welch'
author_email = 'welch18@vt.edu'
url = 'https://almanac.brianwel.ch'

with open(prod_requirements_file, 'r') as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(version_file, encoding='utf-8') as f:
    exec(f.read())  # loads __version__ and __version_info__
    version = __version__  # type: ignore  # noqa

with open(readme_file, encoding='utf-8') as f:
    long_description = f.read()
long_description_content_type = 'text/markdown'

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Framework :: AsyncIO',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Typing :: Typed'
]

setup(
    name=pypi_name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    license=license,
    install_requires=install_requires,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    classifiers=classifiers,
    long_description=long_description,
    long_description_content_type=long_description_content_type
)
