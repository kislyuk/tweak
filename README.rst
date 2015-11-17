tweak: Application configuration engine
=======================================
Python helper class to ingest and serialize app-specific configuration

Provides a self-contained (no dependencies outside the standard library), Python 2 and 3 compatible configuration
manager. Automatically saves and restores your application's configuration in your user home directory. Uses JSON
for serialization. Supports dict-like methods and access semantics.

Installation
------------
::

    pip install tweak

Synopsis
--------

.. code-block:: python

    from tweak import Config

    config = Config()
    config.host, config.port = "example.com", 9000
    config.nested_config = {}
    config.nested_config.foo = True

After restarting your application::

    config = Config()
    print(config)
    >>> {'host': 'example.com', 'port': 9000, 'nested_config': {'foo': True}}

Using an ``argparse.Namespace`` object returned by ``argparse.parse_args()``::

    parser = argparse.ArgumentParser()
    ...
    args = parser.parse_args()
    if args.foo is not None:
        config.foo = args.foo
    elif "foo" not in config:
        raise Exception("foo unconfigured")

    config.update(vars(args))

Authors
-------
* Andrey Kislyuk

Links
-----
* `Project home page (GitHub) <https://github.com/kislyuk/tweak>`_
* `Documentation (Read the Docs) <https://tweak.readthedocs.org/en/latest/>`_
* `Package distribution (PyPI) <https://pypi.python.org/pypi/tweak>`_

Bugs
~~~~
Please report bugs, issues, feature requests, etc. on `GitHub <https://github.com/kislyuk/tweak/issues>`_.

License
-------
Licensed under the terms of the `Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_.

.. image:: https://travis-ci.org/kislyuk/tweak.png
        :target: https://travis-ci.org/kislyuk/tweak
.. image:: https://img.shields.io/coveralls/kislyuk/tweak.svg
        :target: https://coveralls.io/r/kislyuk/tweak?branch=master
.. image:: https://img.shields.io/pypi/v/tweak.svg
        :target: https://pypi.python.org/pypi/tweak
.. image:: https://img.shields.io/pypi/dm/tweak.svg
        :target: https://pypi.python.org/pypi/tweak
.. image:: https://img.shields.io/pypi/l/tweak.svg
        :target: https://pypi.python.org/pypi/tweak
.. image:: https://readthedocs.org/projects/tweak/badge/?version=latest
        :target: https://tweak.readthedocs.org/
