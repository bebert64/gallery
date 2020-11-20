# -*- coding: utf-8 -*-
"""
Config module.

Defines a Config class, containing among else the application folder, both when
runnning from python as well as when running from a built .exe file.

Creates an instance, "config", that can be share by all modules from the application.

"""

import sys
from pathlib import Path
import toml
from peewee import SqliteDatabase

# TODO : complete the class docstring for the new attributes
class Config:
    """
    Class designed to hold all parameters needed from init file or to share information
    between various modules within the app.

    Attributes
    ----------
    toml: {string: string}
        A dictionnary created from the config.toml file.
    app_folder: Path
        The path to the application folder.
    database: Peewee.SqliteDatabase
        The database object containing the tags and the objects.
    object:
    """

    def __init__(self):
        if getattr(sys, "frozen", False):
            app_folder = Path(sys.executable).parent
        else:
            import __main__  # pylint: disable=import-outside-toplevel
            app_folder = Path(__main__.__file__).parent.absolute()
        toml_path = app_folder / "config" / "config.toml"
        self.toml = toml.load(str(toml_path.absolute()))
        self.app_folder = app_folder
        self.database = SqliteDatabase(
            self.app_folder / self.toml["database_path"], pragmas={"foreign_keys": 1}
        )
        self.object = {}


config = Config()
