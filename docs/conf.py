"""Sphinx configuration file."""

import codecs
import os
import sys

from datetime import (
    datetime)

# -- Path setup --------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(HERE)
ALMANAC_MODULE_DIR = os.path.join(BASE_DIR, 'almanac')
ALMANAC_VERSION_FILE = os.path.join(ALMANAC_MODULE_DIR, 'version.py')
sys.path.insert(0, BASE_DIR)


# -- Project information -----------------------------------------------------

with codecs.open(ALMANAC_VERSION_FILE, encoding='utf-8') as f:
    exec(f.read())  # loads __version__ and __version_info__

project = 'almanac'
author = 'Brian Welch'
year = datetime.now().year
copyright = f'{year}, {author}'
version = '.'.join(str(i) for i in __version_info__[:2])  # noqa
release = __version__  # noqa
master_doc = 'index'
source_suffix = '.rst'
pygments_style = 'sphinx'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode'
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

autodoc_default_flags = [
    'members',
    'special-members',
    'show-inheritance'
]

suppress_warnings = [
    'image.nonlocal_uri'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = [
    '_templates'
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [
    '_static'
]
