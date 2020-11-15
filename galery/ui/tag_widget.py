# -*- coding: utf-8 -*-
"""
Module defining the TagWidget and its signals TagWidgetSignals.
"""

from PySide2 import QtWidgets, QtCore  # pylint: disable=no-name-in-module


class TagWidget(QtWidgets.QTreeWidgetItem):
    """TagWidget is a label representing a tag, displayed in the TagTreeWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = TagWidgetSignals(self)
        self.name = ""


class TagWidgetSignals(QtCore.QObject):
    """
    TagWidgetSignals are the signals emited by the TagWidget.

    Attributes
    ----------
    dropped: QtCore.Signal
        Signal emited by a TagWidget when the tag has been dragged and dropped over the
        GridWidget.
    tag_widget: TagWidget
        The TagWidget emiting the signal.

    """

    dropped = QtCore.Signal(int)

    def __init__(self, tag_widget):
        super().__init__()
        self.tag_widget = tag_widget
