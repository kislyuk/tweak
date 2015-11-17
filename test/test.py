# config = Config()
# config.test = 1
# config.test2 = True
# config.test3 = None
# #config.test4 = dict(x=1, y=2)
# print(config.test4.x)
# config.test4.x = "тест"
# print(config.test4.x)
# config.test4.save()
# print(config)

config = Config()
print(config)
config.host, config.port = "example.com", 9000
config.nested_config = {}
config.nested_config.foo = True
print(config)
if "token" not in config:
    config["token"] = "x"

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--foo")
parser.add_argument("--bar")
args = parser.parse_args()
config.update(vars(args))
print(config)
