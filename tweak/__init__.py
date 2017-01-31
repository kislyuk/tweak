#!/usr/bin/env python3

from __future__ import print_function, unicode_literals, division, absolute_import

import os, sys, json, errno, collections, atexit, logging, glob

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
    _site_config_home = "/etc"
    _user_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    _logger = logging.getLogger(__name__)

    def __init__(self, name=os.path.basename(__file__), save_on_exit=True, autosave=False, use_yaml=False,
                 allow_includes=False, _parent=None, _data=None):
        """
        :param name:
            Name of the application that this config belongs to. This will be used as the name of the config directory.
        :param save_on_exit: If True, save() will be called at Python interpreter exit (using an atexit handler).
        :param autosave: If True, save() will be called after each attribute assignment.
        :param use_yaml:
            If True, the config file will be interpreted as YAML; otherwise, as JSON. Requires the PyYAML optional
            dependency to be installed.
        """
        self._name, self._save_on_exit, self._autosave, self._use_yaml = name, save_on_exit, autosave, use_yaml
        self._allow_includes = allow_includes
        if save_on_exit:
            atexit.register(self.save)
        self._parent = _parent
        if self._parent is None:
            self._data = {}
            for config_file in self.config_files:
                try:
                    with open(config_file) as fh:
                        self._load(fh)
                except Exception as e:
                    self._logger.debug(e)
        else:
            self._data = _data

    @property
    def config_files(self):
        config_files = [
            os.path.join(self._site_config_home, self._name, "config.yml" if self._use_yaml else "config.json"),
            os.path.join(self._user_config_home, self._name, "config.yml" if self._use_yaml else "config.json")
        ]
        config_var = self._name.upper() + "_CONFIG_FILE"
        if config_var in os.environ:
            config_files.extend(os.environ[config_var].split(":"))
        return config_files

    def update(self, *args, **kwargs):
        updates = collections.OrderedDict()
        updates.update(*args, **kwargs)
        for k, v in updates.items():
            if isinstance(v, collections.Mapping):
                try:
                    if len(v) == 1 and list(v.keys())[0] == "$append":
                        self[k].append(list(v.values())[0])
                    elif len(v) == 1 and list(v.keys())[0] == "$extend":
                        self[k].extend(list(v.values())[0])
                    elif len(v) == 1 and list(v.keys())[0] == "$insert":
                        for position, value in list(v.values())[0].items():
                            self[k].insert(position, value)
                    elif len(v) == 1 and list(v.keys())[0] == "$extendleft":
                        self[k][0:0] = list(v.values())[0]
                    elif len(v) == 1 and list(v.keys())[0] == "$remove":
                        self[k].remove(list(v.values())[0])
                    else:
                        if k not in self:
                            self[k] = {}
                        self[k].update(v)
                except Exception as e:
                    self._logger.debug(e)
            else:
                self[k] = updates[k]

    def _parse(self, stream):
        if self._use_yaml:
            import yaml

            class ConfigLoader(yaml.Loader):
                def construct_mapping(loader, node):
                    loader.flatten_mapping(node)
                    return self._as_config(yaml.Loader.construct_mapping(loader, node))
            ConfigLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, ConfigLoader.construct_mapping)
            return yaml.load(stream, ConfigLoader) or {}
        else:
            return json.load(stream, object_hook=self._as_config)

    def _load(self, stream):
        contents = self._parse(stream)
        if self._allow_includes and "include" in contents:
            includes = contents["include"] if isinstance(contents["include"], (list, tuple)) else [contents["include"]]
            for include in includes:
                for include_file in glob.glob(os.path.join(os.path.dirname(stream.name), include)):
                    try:
                        with open(include_file) as fh:
                            self._load(fh)
                    except Exception as e:
                        self._logger.debug(e)
            del contents["include"]
        self.update(contents)
        self._logger.info("Loaded configuration from %s", stream.name)

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
            return Config(save_on_exit=self._save_on_exit, autosave=self._autosave, _parent=self, _data=d)
        return d

    def save(self, mode=0o600):
        """
        Serialize the config data to the user home directory.

        :param mode: The octal Unix mode (permissions) for the config file.
        """
        if self._parent is not None:
            self._parent.save(mode=mode)
        else:
            config_dir = os.path.dirname(os.path.abspath(self.config_files[-1]))
            try:
                os.makedirs(config_dir)
            except OSError as e:
                if not (e.errno == errno.EEXIST and os.path.isdir(config_dir)):
                    raise
            with open(self.config_files[-1], "wb" if sys.version_info < (3, 0) else "w") as fh:
                self._dump(fh)
            os.chmod(self.config_files[-1], mode)
            self._logger.debug("Saved config to %s", self.config_files[-1])

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
