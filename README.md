<p align="center">
  <img width="600" height="162" src="https://github.com/welchbj/almanac/blob/master/static/logo.png?raw=true" alt="almanac logo">
</p>
<p align="center">
  <em>a framework for interactive, page-based console applications</em>
</p>
<p align="center">
  <a href="https://travis-ci.org/welchbj/almanac">
    <img src="https://img.shields.io/travis/welchbj/almanac/develop.svg?style=flat-square&label=ci" alt="ci status">
  </a>
  <a href="https://pypi.org/project/almanac/">
    <img src="https://img.shields.io/pypi/v/almanac.svg?style=flat-square&label=pypi" alt="pypi">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.8+-b042f4.svg?style=flat-square" alt="python version">
  </a>
</p>

---

## Synopsis

This framework aims to serve as an intuitive interface for spinning up interactive page-based console applications.

## Installation

You can download the latest packaged version from PyPI:
```sh
pip install almanac
```

Alternatively, you can get the bleeding-edge version from version control:
```sh
pip install https://github.com/welchbj/almanac/archive/master.tar.gz
```

## License

The original content of this repository is licensed under the [MIT License](https://opensource.org/licenses/MIT), as per the [LICENSE.txt](./LICENSE.txt) file.

Some of the parsing logic is borrowed from the [python-nubia](https://github.com/facebookincubator/python-nubia) project and is licensed under that project's [BSD License](https://github.com/facebookincubator/python-nubia/blob/master/LICENSE). For more information, please see the comment in [`almanac/parsing/parsing.py`](almanac/parsing/parsing.py).

## Development

Development dependencies can be installed with:

```sh
pip install -r deps/dev-requirements.txt
```

To run the tests, use:

```sh
python tasks.py test
```

To lint and type check the code, use:

```sh
flake8 .
mypy .
```

When it's time to cut a release, use:

```sh
python setup.py bdist_wheel sdist
twine check dist/*.whl dist/*.gz
twine upload dist/*.whl dist/*.gz
```