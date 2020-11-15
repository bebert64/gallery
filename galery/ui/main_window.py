# -*- coding: utf-8 -*-
"""
Module defining the MyMainWindow widget.

"""

from PySide2 import QtWidgets
from .grid_widget_container import GridWidgetContainer
from .factory import Factory
from .tag_tree_widget import TagTreeWidget
from models.tags import Tag, ObjectTag

# from models.my_object import MyObject


class MyMainWindow(QtWidgets.QMainWindow, Factory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_widget_container = None
        self.tag_tree_widget = None
        self.tag_widgets = []

    def finish_init(self):
        """Finishes the initialization after the widget has been created."""
        self.add_tag_tree_widget()
        self.add_grid_widget()

    def add_grid_widget(self):
        self.grid_widget_container = GridWidgetContainer.create_widget(parent=self)
        self.grid_widget_container.main_window = self
        self.grid_scrollarea.setWidget(self.grid_widget_container)
        self.grid_widget_container.repaint()

    def add_tag_tree_widget(self):
        self.tag_tree_widget = TagTreeWidget.create_widget(parent=self)
        print(self.tag_tree_widget)
        self.tag_tree_widget.signals.dropped.connect(self.drag_drop_event)
        self.tree_and_grid_container.layout().insertWidget(0, self.tag_tree_widget)

    def resizeEvent(self, _):
        self.grid_widget_container.repaint()

    def drag_drop_event(self, cell_number, tag_id):
        if cell_number in self.grid_widget.selection:
            cells_dragged = self.grid_widget.selection
        else:
            cells_dragged = [cell_number]
        for cell_index in cells_dragged:
            cell = self.grid_widget.cells[cell_index]
            print("\nfrom main window")
            tag = Tag.get(Tag.id == tag_id)
            ObjectTag.get_or_create(video=cell.video, tag=tag)
