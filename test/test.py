#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os, sys, unittest, tempfile, json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tweak import Config

class TestTweak(unittest.TestCase):
    def test_basic_statements(self):
        config = Config()
        print(config)
        config.host, config.port = "example.com", 9000
        config.nested_config = {}
        config.nested_config.foo = True
        config.nested_config.bar = 9000
        print(config)
        if "token" not in config:
            config["token"] = "т"

        import argparse
        parser = argparse.ArgumentParser(description=__doc__)
        for arg in "verbose quiet failfast catch buffer".split():
            parser.add_argument("-" + arg[0], "--" + arg, nargs="?")
        parser.add_argument("--foo")
        parser.add_argument("--bar")
        args = parser.parse_args()
        config.update(vars(args))
        print(config)

        config = Config(save_on_exit=True, autosave=False, use_yaml=True)
        config.foo = "bar"
        config.nested_config = {}
        config.nested_config.foo = True
        config.nested_config.bar = 9001
        config.nested_config.baz = "т"

    def test_basic_statements2(self):
        config = Config()
        config.test = 1
        config.test2 = True
        config.test3 = None
        config.test4 = dict(x=1, y=2)
        print(config.test4.x)
        config.test4.x = "тест"
        print(config.test4.x)
        config.test4.save()
        print(config)

    def test_merge(self):
        config = Config()
        config.update({})
        config.update({"m": {"i": 1}})
        self.assertEqual(config["m"], {"i": 1})
        config.update({"m": {"j": 2}})
        self.assertEqual(config["m"], {"i": 1, "j": 2})
        config.update({"m": {"j": [7, 8]}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8]})
        config.update({"m": {"k": []}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": []})
        config.update({"m": {"k": {"$append": "v"}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": ["v"]})
        config.update({"m": {"k": {"$append": "v"}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": ["v", "v"]})
        config.update({"m": {"k": {"$extend": ["z", "z"]}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": ["v", "v", "z", "z"]})
        config.update({"m": {"k": {"$extendleft": ["z", "z"]}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": ["z", "z", "v", "v", "z", "z"]})
        config.update({"m": {"k": {"$insert": {0: 5}}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": [5, "z", "z", "v", "v", "z", "z"]})
        config.update({"m": {"k": {"$remove": "z"}}})
        self.assertEqual(config["m"], {"i": 1, "j": [7, 8], "k": [5, "z", "v", "v", "z", "z"]})

    def test_ingest(self):
        with tempfile.NamedTemporaryFile("w") as cf1, tempfile.NamedTemporaryFile("w") as cf2:
            json.dump(dict(x="foo", y="bar", z={}), cf1)
            cf1.flush()
            json.dump(dict(x=list(range(8)), z={None: None}, t=4.5), cf2)
            cf2.flush()
            os.environ["TWEAK_TEST_CONFIG_FILE"] = ":".join([cf1.name, cf2.name])
            config = Config("TWEAK_TEST")
            self.assertEqual(dict(config), {'y': 'bar', 'x': list(range(8)), 'z': {'null': None}, 't': 4.5})
            self.assertEqual(len(config.config_files), 4)

    def test_include(self):
        with tempfile.NamedTemporaryFile("w") as cf1, tempfile.NamedTemporaryFile("w") as cf2:
            json.dump(dict(x="foo", y="bar", z={}), cf1)
            cf1.flush()
            incl_expr = os.path.basename(cf1.name) + "*"
            json.dump(dict(x=list(range(8)), z={None: None}, t=4.5, include=incl_expr), cf2)
            cf2.flush()
            os.environ["TWEAK_TEST_CONFIG_FILE"] = cf2.name
            config = Config("TWEAK_TEST", allow_includes=True)
            self.assertEqual(dict(config), {'y': 'bar', 'x': list(range(8)), 'z': {'null': None}, 't': 4.5})
            self.assertEqual(len(config.config_files), 3)
            config = Config("TWEAK_TEST")
            self.assertEqual(dict(config), {'x': list(range(8)), 'z': {'null': None}, 't': 4.5, 'include': incl_expr})
            self.assertEqual(len(config.config_files), 3)

if __name__ == '__main__':
    unittest.main()
