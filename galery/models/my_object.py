# -*- coding: utf-8 -*-

from importlib import import_module
from config.config import config

# MyObject = import_module(
#     config.toml["object_class_name"], config.toml["object_package"]
# )

my_object_module = import_module(config.toml["object_package"])
MyObject = getattr(my_object_module, config.toml["object_class_name"])
