tweak: Application configuration engine
=======================================
Python helper class to ingest and serialize app-specific configuration

Provides a self-contained (no dependencies outside the standard library), Python 2 and 3 compatible configuration
manager. Automatically saves and restores your application's configuration in your user home directory. Uses JSON or
(optionally) YAML for serialization. Supports dict-like methods and access semantics.

Installation
------------
If your package does not permit dependency management, you can copy the ``Config`` class directly into your
application from https://github.com/kislyuk/tweak/blob/master/tweak/__init__.py. Otherwise:

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

Using YAML::

    config = Config(use_yaml=True)
    ...

Pass ``Config(save_on_exit=False)`` to disable automatic configuration saving on Python shutdown (this is useful if you
only want to read the config, never write it, or if you want to call ``config.save()`` manually). Pass
``Config(autosave=True)`` to make ``save()`` run any time an assignment happens to a config object.

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
