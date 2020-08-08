=================
Development Guide
=================

------------------------------------
Setting up a development environment
------------------------------------

TODO

-------
Testing
-------

Overview
~~~~~~~~

TODO

Doctests
~~~~~~~~

Code examples are scattered throughout the framework's docstrings, in the format expected by Python's :py:mod:`doctest` module.

To test all of the doctests (across the library code and the documentation site sources), use:

.. code-block:: shell

   pytest almanac/ docs/

Unit tests
~~~~~~~~~~

To run all of the unit tests, use:

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

TODO

--------
Releases
--------

TODO