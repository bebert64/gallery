# -*- coding: utf-8 -*-

"""Module managing the icons."""

from enum import Enum
from pathlib import Path
from typing import Dict, Type, Union

from PySide6 import QtGui

from gallery.config.config import Config

_icons: Dict[str, QtGui.QIcon] = {}
_pixmaps: Dict[str, QtGui.QPixmap] = {}
_package_folder = Config.get_package_folder()

ResourceType = Union[QtGui.QIcon, QtGui.QPixmap]
ResourceDict = Dict[str, ResourceType]


class ResourceDefinition(Enum):

    """Available resources obtainable through specific methods."""

    icon = (_icons, QtGui.QIcon)
    pixmap = (_pixmaps, QtGui.QPixmap)


def _get_resource(name: str, resource_definition: ResourceDefinition) -> ResourceType:
    resource_dict, resource_class = resource_definition.value
    try:
        resource = resource_dict[name]
    except KeyError:
        resource = _add_new_resource(name, resource_dict, resource_class)
    return resource


def _add_new_resource(
    name: str, resource_dict: ResourceDict, resource_class: Type[ResourceType]
) -> ResourceType:
    resource = _create_resource(name, resource_class)
    resource_dict[name] = resource
    return resource


def _create_resource(name: str, resource_class: Type[ResourceType]):
    resource_file_path = _get_resource_file_path(name)
    _check_resource_file_exists(resource_file_path)
    resource = resource_class(str(resource_file_path))
    return resource


def _get_resource_file_path(name: str) -> Path:
    resource_folder_path = _package_folder / "widgets" / "icons"
    resource_file_name = name + ".xpm"
    resource_file_path = resource_folder_path / resource_file_name
    return resource_file_path


def _check_resource_file_exists(resource_file_path: Path) -> None:
    if not resource_file_path.exists():
        raise FileNotFoundError(
            f"No resource file has been found : {resource_file_path}"
        )


def get_icon(name: str) -> QtGui.QIcon:
    """
    The icon matching the name.

    Error
    -----
    FileNotFoundError
        If no file matching the name is found in the subfolder (package folder / gui
        / icons).
    """
    icon = _get_resource(name, ResourceDefinition.icon)
    return icon


def get_pixmap(name: str) -> QtGui.QPixmap:
    """
    The pixmap matching the name.

    Error
    -----
    FileNotFoundError
        If no file matching the name is found in the subfolder (package folder / gui
        / icons).
    """
    pixmap = _get_resource(name, ResourceDefinition.pixmap)
    return pixmap
