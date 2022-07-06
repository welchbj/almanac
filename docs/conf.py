"""Sphinx configuration file."""

import codecs
import os
import sys
from datetime import datetime

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

language = 'en'
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
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'prompt_toolkit': ('https://python-prompt-toolkit.readthedocs.io/en/master/', None)
}

autodoc_default_options = {
    'members': True,
    'show-inheritance': True
}

napoleon_use_param = True

suppress_warnings = [
    'image.nonlocal_uri'
]

templates_path = [
    '_templates'
]

exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]

# -- Formatting options ------------------------------------------------------

add_module_names = False

# -- HTML ouput options ------------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': 'https://almanac.brianwel.ch/',
    'logo_only': True
}
html_title = f'almanac ({version})'
html_static_path = [
    '_static',
]
html_logo = '_static/logo-white.png'

# TODO
# html_favicon = 'TODO'
