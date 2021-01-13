# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

 The CellDimension acceptable values.

"""

import pathlib
import sys
from copy import copy
from enum import Enum
from typing import Type, Any, Dict, Optional, Union, List

import peewee
import toml
from gallery.models.tags import tag_factory
from gallery.models.views import View

Option = Union[int, str]
Options = Dict[str, Option]


class CellDimension(Enum):

    """
    The acceptable cell dimensions values.

    The dimensions for cells are defined relatively to the default dimensions, given in
    the config.toml file. Those default values can be overridden by passing options
    to the Config object when creating it.

    Attributes
    ----------
    small
    medium
    large
    extra_large

    """

    small: float = 0.75
    """A small cell will have dimensions 75% those of default."""

    medium: float = 1
    """A medium cell will have default dimensions."""

    large: float = 1.25
    """A large cell will have dimensions 25% larger than default."""

    extra_large: float = 1.5
    """A extra large cell will have dimensions 50% larger than default."""


class Config:
    """
    The Config object holds information we need to share among the various objects.

    All values from the config.toml file are added as attribute at runtime.

    Parameters
    ----------
    database
        The database holding the peewee objects.
    MyObject
        The model for the user defined object.
    options
        A dictionary containing additional configuration parameters. If a given
        parameter has the same name as one from the config.toml file, the new value
        will superseed the existing one.

    Instance Attributes
    -------------------
    MyTag
    MyObjectTag
    MyView
    cell_dimension
    cell_width
    cell_height

    Methods
    -------
    get_package_folder

    Error
    -----
    AttributeError
        A few names are reserved, and an error will be raised if they are found in
        the options dictionary.

    """

    MyTag: Type[peewee.Model]
    """Model of a tag specific to MyObject, linked to the database given by the user."""

    MyObjectTag: Type[peewee.Model]
    """Model of the link between MyObject and MyTag."""

    MyView: Type[View]
    """Model of a view, linked to the database given by the user."""

    cell_dimension: CellDimension = CellDimension.medium

    def __init__(
        self,
        database: peewee.SqliteDatabase,
        MyObject: Type[peewee.Model],
        options: Optional[Options] = None,
    ):
        self.database: peewee.SqliteDatabase = database
        self.MyObject: Type[peewee.Model] = MyObject
        self._add_tag_related_attributes()
        self._reserved_attribute_names: List[str] = self._get_reserved_attribute_names()
        self._add_attributes_from_toml_file()
        self._add_attributes_from_options(options)

    def _get_reserved_attribute_names(self) -> List[str]:
        # To include all reserved names, must be run AFTER _add_tag_related_attributes
        return copy(list(self.__dict__.keys()))

    # By default, mypy complains that the attributes created dynamically by
    # the _add_attributes_from_toml_file method do not exist.
    # redefining __getattr__ with types makes mypy stop complaining.
    def __getattr__(self, name: str) -> Any:
        try:
            getattr(super(), name)
        except AttributeError as error:
            raise AttributeError(
                f"Parameter {name} has not been found in the config.toml file."
            ) from error

    @staticmethod
    def get_package_folder() -> pathlib.Path:
        """
        The path to the package folder.

        If the package has been bundled in a .exe file, returns the application folder.
        """
        is_application_frozen = getattr(sys, "frozen", False)
        if is_application_frozen:
            package_path = Config._get_frozen_package_path()
        else:
            package_path = Config._get_unfrozen_package_path()
        return package_path

    @staticmethod
    def _get_frozen_package_path() -> pathlib.Path:
        app_file_path = pathlib.Path(sys.executable)
        package_path = app_file_path.parent
        return package_path

    @staticmethod
    def _get_unfrozen_package_path() -> pathlib.Path:
        file_path = pathlib.Path(__file__)
        config_folder_path = file_path.parent
        package_path = config_folder_path.parent
        return package_path

    def _add_tag_related_attributes(self) -> None:
        self._add_attributes_linked_to_my_object()
        self._add_view_attribute()

    def _add_view_attribute(self) -> None:
        self.MyView = View
        self.MyView._meta.database = (  # pylint: disable = no-member, protected-access
            self.database
        )

    def _add_attributes_linked_to_my_object(self) -> None:
        self.MyTag, self.MyObjectTag = tag_factory(self.database, self.MyObject)
        self.MyObject.MyTag = self.MyTag
        self.MyObject.MyObjectTag = self.MyObjectTag

    def _add_attributes_from_toml_file(self) -> None:
        toml_file_path = self.get_package_folder() / "config" / "config.toml"
        toml_dict = toml.load(toml_file_path)
        for attribute_name, attribute_value in toml_dict.items():
            self._add_attribute(attribute_name, attribute_value)

    def _add_attributes_from_options(self, options: Optional[Options]):
        if options is not None:
            for attribute_name, attribute_value in self.options.items():
                self._add_attribute(attribute_name, attribute_value)

    def _add_attribute(self, attribute_name: str, attribute_value: Any) -> None:
        is_attribute_reserved = self._is_attribute_reserved(attribute_name)
        if is_attribute_reserved:
            self._raise_attribute_exists_error(attribute_name)
        setattr(self, attribute_name, attribute_value)

    def _is_attribute_reserved(self, attribute_name):
        return attribute_name in self._reserved_attribute_names

    def _raise_attribute_exists_error(self, attribute_name: str) -> None:
        error_message = f"""
The attribute name "{attribute_name}" is reserved by the config file, and cannot be
given to any attribute from the config.toml file. Please rename it before restarting
the application."""
        error_message_formatted = self._format_error_message(error_message)
        raise AttributeError(error_message_formatted)

    @staticmethod
    def _format_error_message(error_message: str) -> str:
        return error_message.replace("\n", " ").strip()

    @property
    def cell_width(self) -> int:
        """The width of a cell in pixels."""
        zoom = self.cell_dimension.value
        return int(self.cell_width_default * zoom)

    @property
    def cell_height(self) -> int:
        """The height of a cell in pixels."""
        zoom = self.cell_dimension.value
        return int(self.cell_height_default * zoom)
