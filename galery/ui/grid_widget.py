# -*- coding: utf-8 -*-
"""Module defining the GridWidget class."""


# from config.config import config
from PySide2 import QtCore, QtWidgets

from models.my_object import MyObject
from models.tags import ObjectTag
from .cell_widget import CellWidget
from .factory import Factory
from .tag_tree_widget import TagTreeWidget
from .grid_parameters import grid_parameters


class GridWidget(QtWidgets.QWidget, Factory):

    """
    The GridWidget is a scrollable grid with cells represeting the user defined objects.

    Attributes
    ----------
    cells:
        List of the cells currently displayed in the widget
    objects:
        List of the objects to de displayed in the grid.
    selection:
        List of indexes of the objects selected.
    """

    def __init__(self, *args, objects=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = None
        self.setAcceptDrops(True)
        self.cells = []
        if objects is None:
            self.objects = []
        else:
            self.objects = objects
        self.selection = []

    def finish_init(self):
        self.get_objects()

    def get_objects(self):
        for i in range(500):
            self.objects.append(MyObject(id=i))
        grid_parameters.cells_qty = len(self.objects)

    def create_cell(self, object_index):
        """Creates the cell corresponding to the object_index."""
        if not self.objects:
            return
        my_object = self.objects[object_index]
        # The cell index will be len(self.cells) just before we append it (as list
        # numbering starts at 0 in python)
        # cell_index = len(self.cells)
        cell = CellWidget.create_widget(my_object, parent=self)
        cell.signals.clicked.connect(self.cell_clicked)
        self.cells.append(cell)
        if cell.object.id in self.selection:
            cell.select()

    def repopulate_grid(self):
        row = 0
        column = 0
        for cell in self.cells:
            self.gridLayout.addWidget(cell, row, column)
            if column == grid_parameters.columns_qty - 1:
                column = 0
                row += 1
            else:
                column += 1

    def remove_all_cells(self):
        self.cells = []
        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.itemAt(i).widget().setParent(None)

    def cell_clicked(self):
        cell = self.sender().cell
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        cell.toggle_select()
        if modifiers == QtCore.Qt.ControlModifier:
            if cell.is_selected:
                self.selection.append(cell.object.id)
            else:
                self.selection.remove(cell.object.id)
        else:
            self.selection = [cell.object.id]
            for other_cell in [
                other_cell for other_cell in self.cells if other_cell != cell
            ]:
                other_cell.unselect()

    def dragEnterEvent(self, event):
        if isinstance(event.source(), TagTreeWidget):
            event.accept()

    def dropEvent(self, event):
        tag = event.source().selectedItems()[0].tag
        if tag.name == "Tout":
            self.objects = list(MyObject.select())
        else:
            self.objects = list(
                MyObject.select()
                .join(ObjectTag)
                .where(ObjectTag.tag_id == tag.id)  # pylint: disable=no-member
                .order_by(MyObject.id)
            )
        self.remove_all_cells()
        self.get_videos()
        self.repaint(force=True)

    # def add_row(self):
    #     return
    #     if not self.objects:
    #         return
    #     self.visible_row_first += 1
    #     self.repaint(True)
    #     self.main_window.grid_widget_container.repaint()
    #     # for column in range(self.columns_grid):
    #     #    self.create_cell()
    #     #    last_cell = self.cells[-1]
    #     #    self.gridLayout.addWidget(last_cell, self.rows_grid, column)
    #     # widget_width_new = GridWidget.COLUMN_WIDTH * self.columns_grid
    #     # widget_height_new = GridWidget.ROW_HEIGHT * self.rows_grid
    #     # self.resize_grid(widget_height_new, widget_width_new)

    # def remove_row(self):
    #     return
    #     if not self.objects:
    #         return
    #     self.visible_row_first -= 1
    #     self.repaint(True)
    #     self.main_window.grid_widget_container.repaint()
