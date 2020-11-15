# -*- coding: utf-8 -*-
"""
Module containg definition for the CellWidget and CellSignals classes.
"""

from PySide2 import QtCore, QtGui, QtWidgets
from config.config import config
from .factory import Factory
from .menus import CellMenu


class CellWidget(QtWidgets.QWidget, Factory):

    """
    A single cell in the galery, representing a user-defined object.

    If the object has a thumbnail_path method, it can be used to give the cell the
    path to a thumbnail image, displayed on the cell background.

    Attributes
    ----------
    index: integer
        The unique identifier used by the rest of the application to identy the cell.
    object: object
        The user defined object the cell represents.
    signals:
        Signals used to communicate with the rest of the application.
    is_selected:
        Whether the cell is selected or not.
    position_at_click: QPoint
        Coordinates of the mouse at the moment it is clicked.
    is_mouse_down: boolean
        Whether the mouse is clicked or not.
    overlay: QLabel
        An overlay that can be hidden or shown, to indicate the cell is selected.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = 0
        self.object = None
        self.signals = CellSignals(self)
        self.is_selected = False
        self.position_at_click = None
        self.is_mouse_down = False
        self.overlay = None

    def finish_init(self, index, my_object):
        """
        Finishes the initialization, after the widget is created.

        This function is provided by the Factory class.

        Attributes
        ----------
        index: integer
            An index used by the application to identify the cell.
        my_object: any
            User defined object represented by the cell.
        """

        self.object = my_object
        self.index = index
        self.add_overlay()
        self.add_image()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        # if not self.parent():
        #     print(f"Cell without parent : {self.object.id}")
        # else:
        #     print(f"Cell  with parent : {self.object.id} / {self.parent()}")

    def add_overlay(self):
        """
        Adds a transparent overlay that can be hidden or shown.

        The overlay is used to indicate that the cell is part of the current selection.
        Its color is defined by the cell_overlay_color parameter in the config file.

        """
        self.overlay = QtWidgets.QLabel(self)
        self.overlay.setStyleSheet(
            f"background-color: {config.toml['cell_overlay_color']};"
        )
        self.overlay.setFixedSize(self.size())
        self.overlay.hide()

    def add_image(self):
        """If possible, adds an image to the cell background."""
        if hasattr(self.object, "thumbnail_path"):
            thumbnail_path = self.object.thumbnail_path()
            background_image = QtGui.QPixmap(str(thumbnail_path))
            self.label.setPixmap(background_image)
            self.label.setScaledContents(True)
        else:
            self.label.setText(str(self.object.id))

    def mousePressEvent(self, event):
        """
        Intercept the mouse position and updates the is_mouse_down flag.

        Attributes
        ----------
        event: QEvent
            The mousePressEvent passed by QT.

        """
        if event.button() == QtCore.Qt.LeftButton:
            self.position_at_click = event.pos()
            self.is_mouse_down = True

    def mouseMoveEvent(self, event):
        """
        Initiates the drag action when checks are validated.

        Computes the drag distance since the mouse was clicked, and initiates the
        drag action if that distance is superior to the parameter found in the
        config file.
        The drag is initiated with a text mimeData, formated to contain the cell
        index and information about the object.

        Attributes
        ----------
        event: QEvent
            The mouseMoveEvent passed by QT.

        """
        drag_distance = (event.pos() - self.position_at_click).manhattanLength()
        if (
            self.is_mouse_down
            and drag_distance >= config.toml["cell_min_drag_distance"]
        ):
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(f"{self.index}#{self.object.id}")
            drag.setMimeData(mime_data)
            drag.exec_()

    def mouseReleaseEvent(self, event):
        """
        Emits a signal if the cell has been clicked.

        Attributes
        ----------
        event: QEvent
            The mouseReleaseEvent passed by QT.

        """
        if event.button() == QtCore.Qt.LeftButton:
            self.is_mouse_down = False
            if self.position_at_click == event.pos():
                self.signals.clicked.emit()
        super().mouseReleaseEvent(event)

    def toggle_select(self):
        """Toggles between selected and unselected state."""
        if self.is_selected:
            self.unselect()
        else:
            self.select()

    def select(self):
        """Changes display to indicate the cell is selected."""
        self.is_selected = True
        self.overlay.show()

    def unselect(self):
        """Changes display to indicate the cell is unselected."""
        self.is_selected = False
        self.overlay.hide()

    def contextMenuEvent(self, event):
        """Implements the context menu."""
        menu = CellMenu(self)
        menu.exec_(self.mapToGlobal(event.pos()))


class CellSignals(QtCore.QObject):

    """
    Collection of signals used by the CellWidget.

    Attributes
    ----------
    clicked: QtCore.Signal
        A signal emited when the cell is clicked.
    """

    clicked = QtCore.Signal()

    def __init__(self, cell):
        super().__init__()
        self.cell = cell
