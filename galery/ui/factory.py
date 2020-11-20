# -*- coding: utf-8 -*-
"""
Module defining the Factory helper class.
"""


from PySide2 import QtCore, QtUiTools
from config.config import config


class Factory:

    """
    A helper class to create QT object from .ui files.

    ATTRIBUTES
    ----------
    loader:
        The loader is only created once and should never be called directly. Use
        create_widget function instead.
    UI_FILE_NAME: string
        The name of the ui file to use. If UI_FILE_NAME is not initialized by the
        derived class, the loader will try to read from a ui file with the same
        base name as the module itself.
        Ex: MyMainWindow is defined in the module main_window.py => the loader will try
        to load main_window.ui.

    METHODS
    -------
    create_widget
    finish_init: optional
        In some (most ?) cases, we need to do some actions AFTER the widget is created,
        to access its attributes. The finish_init is called after the widget creation,
        during create_widget. Arguments passed to create_widget will in turn be passed
        to finish_init.

    """

    loader = None
    UI_FILE_NAME = None

    @classmethod
    def create_widget(cls, *args, **kwargs):
        """
        Creates a widget from the ui file name UI_FILE_NAME.

        Returns
        -------
        Widget
            The widget created from the ui file.

        """
        if cls.UI_FILE_NAME is None:
            cls.UI_FILE_NAME = cls.__module__.split(".")[-1] + ".ui"
        if cls.loader is None:
            # print(f"creating loader for {cls}")
            cls.loader = QtUiTools.QUiLoader()
            cls.loader.registerCustomWidget(cls)
        ui_file = QtCore.QFile(str(config.app_folder / "ui" / cls.UI_FILE_NAME))
        ui_file.open(QtCore.QFile.ReadOnly)
        parent = kwargs.get("parent")
        widget = cls.loader.load(ui_file, parent)
        try:
            del kwargs["parent"]
        except KeyError:
            print(f"class without parent : {cls}")
        ui_file.close()
        if hasattr(cls, "finish_init"):
            widget.finish_init(*args, **kwargs)
        return widget
