=================
Development Guide
=================

------------------------------------
Setting up a development environment
------------------------------------

It is recommended to conduct development of this library in a `virtual environment <https://docs.python.org/3/library/venv.html>`_.

To install the development dependencies, use:

.. code-block:: shell

   pip install -r deps/dev-requirements.txt

-------
Testing
-------

Overview
~~~~~~~~

``almanac``'s testing strategy is split up into two categories: documentation tests and unit tests. Documentation tests mainly serve to verify that the code examples in the Python docstrings and in the documentation site do not become out of date. This is a nice complement to the unit tests, which enforce the public contract of this framework.

Doctests
~~~~~~~~

Code examples are scattered throughout the framework's docstrings, in the format expected by Python's :py:mod:`doctest` module.

To test all of the doctests (across the library code and the documentation site sources), use:

.. code-block:: shell

   pytest almanac/ docs/

Unit tests
~~~~~~~~~~

Unit tests are written to be executed via `pytest <https://docs.pytest.org/en/stable/>`_. To run all of the unit tests, use:

.. code-block:: shell

   pytest tests/

To run a collection of unit tests, use something like:

.. code-block:: shell

   pytest tests/test_app_configuration.py

To run a single unit test, use something like:

.. code-block:: shell

   pytest tests/test_app_configuration.py -k "test_prompt_str_customization"

-------
Linting
-------

All of the code in this framework is style-linted with `flake8 <https://flake8.pycqa.org/en/latest/>`_ and type-linted with `mypy <https://mypy.readthedocs.io/en/stable/>`_. An `EditorConfig <https://editorconfig.org/>`_ configuration file is also included in the root of this project's repository to aid in style-conforming automatic formatting.

Running the linters is fairly straightforward:

.. code-block:: shell

   flake8 .
   mypy .

--------
Releases
--------

Release builds are performed using `setuptools <https://setuptools.readthedocs.io/en/latest/>`_, with the extra layer of convenience provided by `twine <https://twine.readthedocs.io/en/latest/>`_.

When it's time to cut a release, use the following steps:

.. code-block:: shell

   # Build the source tarball and wheel.
   python setup.py bdist_wheel sdist

   # Verify that PyPI will accept our upload.
   twine check dist/*.whl dist/*.gz

   # Upload to PyPI.
   twine upload dist/*.whl dist/*.gz