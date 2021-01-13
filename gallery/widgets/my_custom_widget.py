# -*- coding: utf-8 -*-

"""
Defines :
 The MyCustomWidget class, a convenience base class with generic functions. The derived
 class must also inherit from a QtWidgets.QWidget.

"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional, Type, TypeVar

import peewee
from PySide6 import QtCore, QtUiTools, QtWidgets

from gallery.config.config import Config
from gallery.models.tags import Tag, ObjectTag

MyType = TypeVar("MyType")


# class MyThread(QtCore.QThread):
#
#     """
#     A QThread executing a function and capable of updating a message box.
#
#     Parameters
#     ----------
#     parent: Union[ShortCutsChild, MainWindow]
#         The parent object, which might itself be a ShortCutsChild, or the
#         first ancestor, which has to be the Main Window.
#     func: Callable
#         The function meant to be run in the separate thread.
#         args
#     *args: Any
#         Variable length argument list, required to run the function.
#     **kwargs: Any
#         Arbitrary keyword arguments, required to run the function.
#     """
#
#     update_message: QtCore.Signal = QtCore.Signal(str)
#     """
#     A signal sent to update the message in the associated message box.
#     """
#
#     update_title: QtCore.Signal = QtCore.Signal(str)
#     """
#     A signal sent to update the title of the associated message box.
#     """
#
#     finished: QtCore.Signal = QtCore.Signal()
#     """
#     A signal sent when the function has finished running.
#     """
#
#     def __init__(self, parent, func, *args, **kwargs):
#         super().__init__()
#         self.parent = parent
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#
#     def run(self):
#         """
#         Executes the function and signals the end.
#         """
#         self.func(self.parent, *self.args, **self.kwargs)
#         self.finished.emit()


class MyCustomWidget:

    """
    A convenience class to create QT object from .ui files.

    MyCustomWidget is meant to be inherited, and cannot be used by itself. The derived
    class must also inherit from a QtWidgets.QWidget. When a widget is created with
    create_widget, if its parent has the attribute MyTag, it will be passe to
    the widget, along MyObject and MyObjectTag.

    Class Attributes
    ----------------
    ui_file_name
    ui_folder_path
    MyTag
    MyObject
    MyObjectTag
    config

    Class Methods
    -------------
    create_widget

    """

    _loader: QtUiTools.QUiLoader
    ui_file_name: str
    """
    The name of the gui file to use. If ui_file_name is not initialized by the
    derived class, the loader will try to read from a .ui file with the same
    base name as the class itself, converted from CamelCase to snake_case.
    Ex: for MainWidget, the loader will try to load main_widget.ui.
    """

    ui_folder_path: Path
    """
    The path to the folder in which to find the .ui files. If not provided by the
    derived class, the "ui_files" sub-folder of the folder where the class is being
    defined will be used.
    """

    MyTag: Type[Tag]
    """Peewee object for the tag specific to the user-designed object."""

    MyObject: Type[peewee.Model]
    """Peewee object for the user-designed object."""

    MyObjectTag: Type[ObjectTag]
    """Peewee object for the links between objects and tags."""

    config: Config
    """The configuration for the widget, shared by all components."""

    @classmethod
    def create_widget(
        cls, parent: Optional[QtWidgets.QWidget] = None
    ) -> MyCustomWidgetMixin:
        """
        Creates a widget based on the .ui file ui_file_name.

        If arguments need to be passed when constructing the derived class, the good
        practice is to define a create_specific_widget in the derived class, itself
        classing super().create_widget()

        Parameters
        ----------
        parent

        Returns
        -------
        MyCustomWidgetMixin
            The widget created based on the .ui file, derived from both MyCustomWidget
            and QtWidgets.QWidget.

        """
        # create_widget is (part of) a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable=protected-access
        widget = cls._create_widget_using_loader(parent)
        assert isinstance(widget, MyCustomWidget)
        assert isinstance(widget, QtWidgets.QWidget)
        widget._set_config()
        return widget

    @classmethod
    def _create_widget_using_loader(
        cls, parent: Optional[QtWidgets.QWidget]
    ) -> MyCustomWidget:
        loader = cls._get_loader()
        ui_file = cls._get_ui_file()
        widget = cls._create_new_widget_from_ui_file(loader, parent, ui_file)
        return widget

    @staticmethod
    def _create_new_widget_from_ui_file(
        loader: QtUiTools.QUiLoader,
        parent: Optional[QtWidgets.QWidget],
        ui_file: QtCore.QFile,
    ) -> QtWidgets.QWidget:
        ui_file.open(QtCore.QFile.ReadOnly)
        widget = loader.load(ui_file, parent)
        ui_file.close()
        return widget

    @classmethod
    def _get_loader(cls) -> QtUiTools.QUiLoader:
        """Initializes the class itself by creating the QUiLoader."""
        if not hasattr(cls, "_loader"):
            cls._loader = QtUiTools.QUiLoader()
            cls._loader.registerCustomWidget(cls)
        return cls._loader

    @classmethod
    def _get_ui_file(cls) -> QtCore.QFile:
        ui_file_name = cls._get_ui_file_name()
        ui_folder_path = cls._get_ui_folder_path()
        ui_file = QtCore.QFile(str(ui_folder_path / ui_file_name))
        return ui_file

    @classmethod
    def _get_ui_file_name(cls) -> str:
        if hasattr(cls, "ui_file_name"):
            ui_file_name = cls.ui_file_name
        else:
            ui_file_name = cls._get_ui_file_name_default()
        return ui_file_name

    @classmethod
    def _get_ui_file_name_default(cls) -> str:
        class_name = cls.__name__
        ui_file_name = cls._camel_case_to_snake_case(class_name) + ".ui"
        return ui_file_name

    @classmethod
    def _get_ui_folder_path(cls) -> Path:
        if hasattr(cls, "ui_folder_path"):
            ui_folder_path = cls.ui_folder_path
        else:
            ui_folder_path = cls._get_ui_folder_path_default()
        return ui_folder_path

    @classmethod
    def _get_ui_folder_path_default(cls) -> Path:
        class_file_path = Path(sys.modules[cls.__module__].__file__)
        class_folder_path = class_file_path.parent
        ui_folder_path = class_folder_path / "ui_files"
        return ui_folder_path

    def _set_config(self) -> None:
        # pylint: disable=no-member
        assert isinstance(self, QtWidgets.QWidget)
        if self.parent() is not None:
            self._set_config_from_parent()

    def _set_config_from_parent(self) -> None:
        # pylint: disable=no-member
        assert isinstance(self, QtWidgets.QWidget)
        if hasattr(self.parent(), "config"):
            self.config = self.parent().config

    def get_ancestor_by_class(
        self, ancestor_class: Type[MyType]
    ) -> Optional[MyType]:
        """
        Gets the closest ancestor of the given class.

        Parameters
        ----------
        ancestor_class
            The class of the ancestor to look for. If no class is given, the parent is
            returned.

        Returns
        -------
        Optional[ancestor_class]
            The closest matching ancestor, or None if no ancestor is found.

        """
        # pylint: disable=no-member
        assert isinstance(self, QtWidgets.QWidget)
        parent = self.parent()
        while not (isinstance(parent, ancestor_class) or parent is None):
            parent = parent.parent()
        return parent

    def get_main_window(self) -> Optional[QtWidgets.QMainWindow]:
        """Returns the closest :class:`QMainWindow` (there should be only one)."""
        return self.get_ancestor_by_class(QtWidgets.QMainWindow)

    @staticmethod
    def _camel_case_to_snake_case(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    @staticmethod
    def create_msg_box(title: str, msg: str) -> None:
        """Creates a simple message box."""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.exec_()


class MyCustomWidgetMixin(QtWidgets.QWidget, MyCustomWidget):
    """Class defined ony for type checking the return value of create_widget."""


#     def set_msg_box_message(self, msg: str):
#         if self.thread is None:
#             self._shortcuts_parent.thread.update_message.emit(msg)
#             return
#         self.thread.update_message.emit(msg)
#
#     def set_msg_box_title(self, title: str):
#         self.thread.update_title.emit(title)
#
#     def handle_thread_finished(self):
#         """
#         Changes the button of the message box to OK.
#
#         The behaviour of the button also changes, from terminating the
#         running thread to simply closing the message box.
#         """
#         self.msg_box.pushButton.setText("OK")
#         self.msg_box.pushButton.clicked.connect(self.msg_box.close)
#
#     def cancel_thread(self):
#         """
#         Cancels the thread and closes the message box.
#         """
#         self.thread.terminate()
#         self.msg_box.close()
#
#
# class MyMsgBox(QtWidgets.QDialog, MyCustomWidget):
#
#     """
#     A simple message box.
#     """
#
#     ui_file_name = "my_msg_box.ui"
#     ui_folder_path = Path(__file__).parent
#
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
#
#
# def display_info_while_running(func):
#     """
#     Executes the function in a separate thread and displays information
#     in a message box.
#     """
#
#     @wraps(func)
#     def wrapper(self, *args, **kwargs):
#         """
#         Wrapper for the function.
#         """
#         self.msg_box = MyMsgBox()
#         self.thread = MyThread(self, func, *args, **kwargs)
#         self.thread.update_message.connect(self.msg_box.label.setText)
#         self.thread.update_title.connect(self.msg_box.setWindowTitle)
#         self.thread.finished.connect(self.msg_box_finished)
#         self.msg_box.pushButton.clicked.connect(self.cancel_thread)
#         self.thread.start()
#         self.msg_box.exec_()
#
#     return wrapper
