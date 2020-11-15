# -*- coding: utf-8 -*-
"""
Module defining the TagTreeWidget and its signals.
"""

import time
from PySide2 import QtWidgets, QtCore, QtGui
from config.config import config
from models.tags import Tag
from .factory import Factory
from .menus import TagMenu
from .tag_widget import TagWidget


# TODO finish documenting the attributes.
class TagTreeWidget(QtWidgets.QTreeWidget, Factory):
    """
    The TagTreeWidget holds the tag's tree, as defined in the database.

    Attributes
    ----------
    tag_hovered: TagWidget

    signals: TagTreeWidgetSignals

    tag_widget_being_edited: TagWidget

    timer_click: integer

    clicked: boolean

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.tag_hovered = None
        self.signals = TagTreeWidgetSignals()
        self.itemDoubleClicked.connect(self.rename_tag)
        self.tag_widget_being_edited = None
        self.timer_click = 0
        self.clicked = False

    def contextMenuEvent(self, event):
        tag_hovered = self.find_tag_hovered(event.pos(), self.invisibleRootItem())
        menu = TagMenu(self, tag_hovered)
        menu.tag_widget = tag_hovered
        menu.exec_(self.mapToGlobal(event.pos()))

    def add_tag_widgets(self):
        tags = Tag.select().where(Tag.parent_id.is_null())  # pylint: disable=no-member
        for tag in tags:
            tag_widget = TagWidget(self)
            tag_widget.tag = tag
            tag_widget.name = tag.name
            tag_widget.setText(0, tag.name)
            self.add_tag_children(tag_widget)

    def add_tag_children(self, tag_widget):
        for child in tag_widget.tag.children:
            child_widget = TagWidget(tag_widget)
            child_widget.name = child.name
            child_widget.tag = child
            child_widget.setText(0, child.name)
            self.add_tag_children(child_widget)

    def finish_init(self):
        self.add_tag_widgets()

    def dragMoveEvent(self, event):
        tag_hovered = self.find_tag_hovered(event.pos(), self.invisibleRootItem())
        try:
            old_name = self.tag_hovered.name
        except AttributeError:
            old_name = "none"
        try:
            new_name = tag_hovered.name
        except AttributeError:
            new_name = "none"
        if old_name != new_name:
            if self.tag_hovered:
                self.tag_hovered.setBackgroundColor(0, QtGui.QColor("white"))
            self.tag_hovered = tag_hovered
            if self.tag_hovered:
                self.tag_hovered.setBackgroundColor(0, QtGui.QColor("lightgreen"))

    def find_tag_hovered(self, mouse_position, item):
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            if self.visualItemRect(child).contains(mouse_position):
                return item.child(i)
            tag_hovered = self.find_tag_hovered(mouse_position, child)
            if tag_hovered:
                return tag_hovered
        return None

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        split_text = event.mimeData().text().split("#")
        try:
            cell_index = int(split_text[0])
        except ValueError:
            print("dropped from tag")
            print(f"{self.selectedItems()[0].name=}")
        else:
            event.accept()
            tag_widget = self.itemAt(event.pos())
            if self.tag_hovered:
                self.tag_hovered.setBackgroundColor(0, QtGui.QColor("white"))
            print("from tag tree")
            print(f"{cell_index=}")
            # print(f"{tag_widget.tag.id=}")
            self.signals.dropped.emit(cell_index, tag_widget.tag.id)

    def rename_tag(self, tag_widget):
        self.tag_widget_being_edited = tag_widget
        self.openPersistentEditor(tag_widget)

    def mouseReleaseEvent(self, _):
        now = time.time()
        if (now - self.timer_click) > config.toml["double_click_time_limit"]:
            self.handle_simple_click()
        self.timer_click = time.time()

    def handle_simple_click(self):
        if self.tag_widget_being_edited:
            if self.isPersistentEditorOpen(self.tag_widget_being_edited):
                self.closePersistentEditor(self.tag_widget_being_edited)
                self.tag_widget_being_edited.tag.name = self.tag_widget_being_edited.text(
                    0
                )
                self.tag_widget_being_edited.tag.save()


class TagTreeWidgetSignals(QtCore.QObject):

    dropped = QtCore.Signal(int, int)
