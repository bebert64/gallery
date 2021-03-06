# -*- coding: utf-8 -*-

"""
Defines :
 The Config class

 The CellDimension acceptable values.

"""

from enum import Enum
from typing import Dict, Optional, Union

from utils.config import Config
from utils.functions import get_data_folder

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


class ConfigGallery(Config):
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
    cell_dimension
    cell_width
    cell_height

    Error
    -----
    AttributeError
        A few names are reserved, and an error will be raised if they are found in
        the options dictionary.

    """

    def __init__(
        self,
        options: Optional[Options] = None,
    ) -> None:
        toml_path = ConfigGallery._get_toml_file_path()
        super().__init__(toml_path, options)
        self.cell_dimension = CellDimension.medium
        self._has_changed_cell_dimension: bool = False

    @staticmethod
    def _get_toml_file_path():
        data_folder = get_data_folder(ConfigGallery)
        toml_file_path = data_folder / "config_gallery.toml"
        return toml_file_path

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

    def change_cell_dimension(self, cell_dimension: CellDimension) -> None:
        """Changes the cells dimension."""
        self.cell_dimension = cell_dimension
        self._has_changed_cell_dimension = True

    def has_changed_cell_dimension(self) -> bool:
        """
        Whether the cell dimension has changed since the last time we drew the grid.
        """
        return self._has_changed_cell_dimension

    def reset_has_changed_cell_dimension(self) -> None:
        """Indicates the cell dimension change has been taken into account."""
        self._has_changed_cell_dimension = False
