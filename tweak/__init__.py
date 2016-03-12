#!/usr/bin/env python3

from __future__ import print_function, unicode_literals, division, absolute_import

import os, sys, json, errno, collections, atexit

class Config(collections.MutableMapping):
    """
    Provides a self-contained (no dependencies outside the standard library), Python 2 and 3 compatible configuration
    manager. Automatically saves and restores your application's configuration in your user home directory. Uses JSON
    or optionally YAML for serialization. Supports dict-like methods and access semantics.

    Examples:

        config = Config()
        config.host, config.port = "example.com", 9000
        config.nested_config = {}
        config.nested_config.foo = True

    After restarting your application:
        config = Config()
        print(config)

        >>> {'host': 'example.com', 'port': 9000, 'nested_config': {'foo': True}}
    """
    _config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

    def __init__(self, name=os.path.basename(__file__), save_on_exit=True, autosave=False, use_yaml=False, _parent=None, _data=None):
        """
        :param name:
            Name of the application that this config belongs to. This will be used as the name of the config directory.
        :param save_on_exit: If True, save() will be called at Python interpreter exit (using an atexit handler).
        :param autosave: If True, save() will be called after each attribute assignment.
        """
        self._config_dir = os.path.join(self._config_home, name)
        self._use_yaml = use_yaml
        self._config_file = os.path.join(self._config_dir, "config.yml" if use_yaml else "config.json")
        if save_on_exit:
            atexit.register(self.save)
        self._autosave = autosave
        self._parent = _parent
        if self._parent is None:
            try:
                with open(self._config_file) as fh:
                    self._load(fh)
            except Exception:
                self._data = {}
        else:
            self._data = _data

    def _load(self, stream):
        if self._use_yaml:
            import yaml
            class ConfigLoader(yaml.Loader):
                def construct_mapping(loader, node):
                    loader.flatten_mapping(node)
                    return self._as_config(yaml.Loader.construct_mapping(loader, node))
            ConfigLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, ConfigLoader.construct_mapping)
            self._data = yaml.load(stream, ConfigLoader) or {}
        else:
            self._data = json.load(stream, object_hook=self._as_config)

    def _dump(self, stream):
        if self._use_yaml:
            import yaml
            def config_representer(dumper, obj):
                return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, obj._data.items())
            yaml.add_representer(self.__class__, config_representer)
            yaml.dump(self._data, stream)
        else:
            json.dump(self._data, stream, default=lambda obj: obj._data)

    def _as_config(self, d):
        if isinstance(d, collections.MutableMapping):
            return Config(autosave=self._autosave, _parent=self, _data=d)
        return d

    def save(self, mode=0o600):
        """
        Serialize the config data to the user home directory.

        :param mode: The octal Unix mode (permissions) for the config file.
        """
        if self._parent is not None:
            self._parent.save(mode=mode)
        else:
            try:
                os.makedirs(self._config_dir)
            except OSError as e:
                if not (e.errno == errno.EEXIST and os.path.isdir(self._config_dir)):
                    raise
            with open(self._config_file, "wb" if sys.version_info < (3, 0) else "w") as fh:
                self._dump(fh)
            os.chmod(self._config_file, mode)

    def __getitem__(self, item):
        if item not in self._data:
            raise KeyError(item)
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = self._as_config(value)
        if self._autosave:
            self.save()

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            self.__dict__[attr] = value
        else:
            self.__setitem__(attr, value)

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        for item in self._data:
            yield item

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)
