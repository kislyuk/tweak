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

Configuration ingestion order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tweak supports ingesting configuration from a configurable array of sources. Each source is a JSON or YAML file.
Configuration sources that follow the first source update the configuration using recursive dictionary merging. Sources are
enumerated in the following order:

- Site-wide configuration source, ``/etc/NAME/config.(yml|json)``
- User configuration source, ``~/.config/NAME/config.(yml|json)``
- Any sources listed in the colon-delimited variable ``NAME_CONFIG_FILE``

Array merge operators
~~~~~~~~~~~~~~~~~~~~~

When loading a chain of configuration sources, Tweak uses recursive dictionary merging to combine the
sources. Additionally, when the original config value is a list, Tweak supports array manipulation operators::

    In [1]: from tweak import Config

    In [2]: c = Config()

    In [3]: c.update(x=[1, 2, 3])

    In [4]: c
    Out[4]: {'x': [1, 2, 3]}

    In [5]: c.update(x={"$append": 4})

    In [6]: c
    Out[6]: {'x': [1, 2, 3, 4]}

    In [7]: c.update(x={"$extend": [5, 6]})

    In [8]: c
    Out[8]: {'x': [1, 2, 3, 4, 5, 6]}

    In [9]: c.update(x={"$appendleft": 0})

    In [10]: c
    Out[10]: {'x': [0, 1, 2, 3, 4, 5, 6]}

    In [11]: c.update(x={"$extendleft": [-2, -1]})

    In [12]: c
    Out[12]: {'x': [-2, -1, 0, 1, 2, 3, 4, 5, 6]}

    In [13]: c.update(x={"$remove": 0})

    In [14]: c
    Out[14]: {'x': [-2, -1, 1, 2, 3, 4, 5, 6]}

Each operator (``$append``, ``$extend``, ``$appendleft``, ``$extendleft``, ``$remove``) must be the only key in the
dictionary representing the update, and the value being updated must be a list. For example, in the following set of two
YAML files, the second file extends the list in the first file.

``/etc/NAME/config.yml``::

    x:
     - y
     - z

``~/.config/NAME/config.yml``::

    x:
     - $extend:
       - a
       - b

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
