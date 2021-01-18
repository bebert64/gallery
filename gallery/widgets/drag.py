# -*- coding: utf-8 -*-

"""
Defines :
 The base class MyDrag.

 The two derived classes DragFromTree and DragFromGrid.

"""

from __future__ import annotations

from typing import List, Dict, Union

from PySide6 import QtGui, QtWidgets, QtCore

import gallery.widgets.grid as grid
import gallery.widgets.icons as icons
import gallery.widgets.main_widget as main_widget
import gallery.widgets.tag_tree as tag_tree
import gallery.types as types

DragSource = Union["grid.TabWidget", "tag_tree.TagTreeWidget"]
Resource = Dict[str, Union[str, bool]]


class MyDrag(QtGui.QDrag):
    """
    Base class for Drag objects.
    """

    _modifiers_dict: Dict[Union[QtCore.Qt.KeyboardModifier, str], Resource] = {}

    def __init__(self, drag_source: DragSource) -> None:
        super().__init__(drag_source)
        self._set_empty_mime_data()
        self._store_self_in_main_widget()

    def _get_resource_from_modifiers(self, resource_name):
        # A QtCore.Qt.KeyboardModifiers is not hashable, and we can't use directly as
        # a key for the dict. However, when checked against a QtCore.Qt.KeyboardModifier
        # (singular...), it does return True.
        # So, we use the KeyboardModifier as key, and check the KeyboardModifiers
        # against all of them.
        resources_dict = self._get_resources_dict_from_modifiers()
        resource = resources_dict[resource_name]
        return resource

    def _get_resources_dict_from_modifiers(self,):
        resources_dict = self._modifiers_dict["Default"]
        keys_modifiers = self._get_keys_modifiers()
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        for key in keys_modifiers:
            if key == modifiers:
                resources_dict = self._modifiers_dict[key]
        return resources_dict

    def _get_keys_modifiers(self):
        keys_modifiers = [
            key
            for key in self._modifiers_dict
            if isinstance(key, QtCore.Qt.KeyboardModifier)
        ]
        return keys_modifiers

    def _get_cursor_name_from_modifiers(self) -> str:
        cursor_name = self._get_resource_from_modifiers("cursor_name")
        return cursor_name

    def _get_method_name_from_modifiers(self) -> str:
        method_name = self._get_resource_from_modifiers("method_name")
        return method_name

    def _get_need_apply_modifiers(self) -> str:
        need_apply_modifiers = self._get_resource_from_modifiers("is_modifier")
        return need_apply_modifiers

    def _set_empty_mime_data(self) -> None:
        mime_data = QtCore.QMimeData()
        self.setMimeData(mime_data)

    def _get_main_widget(self) -> main_widget.MainWidget:
        drag_source = self.source()
        my_main_widget = drag_source.get_ancestor_by_class(main_widget.MainWidget)
        return my_main_widget

    def _get_tag_tree_widget(self) -> tag_tree.TagTreeWidget:
        my_main_widget = self._get_main_widget()
        tag_tree_widget = my_main_widget.tag_tree_widget
        return tag_tree_widget

    def _get_current_tab(self):
        my_main_widget = self._get_main_widget()
        current_tab = my_main_widget.tabs_widget.currentWidget()
        return current_tab

    def _store_self_in_main_widget(self) -> None:
        my_main_widget = self._get_main_widget()
        my_main_widget.drag_object = self

    def _set_cursor_icon(self, icon_name: str, action: QtCore.Qt.DropAction) -> None:
        icon = icons.get_pixmap(icon_name)
        icon_scaled = icon.scaled(25, 25)
        self.setDragCursor(icon_scaled, action)


class DragFromGrid(MyDrag):
    """
    Drag object created from a grid.

    The cursors are modified by the handle_move methods and the result of a drop by
    the handle_drop ones.

    Parameters
    ----------
    cell_widget
        The widget creating the drag object.

    Methods
    -------
    handle_move_on_grid
    handle_drop_on_grid
    handle_move_on_tree
    handle_drop_on_tree

    """

    _modifiers_dict = {
        QtCore.Qt.ShiftModifier: {"cursor_name": "minus",},
        "Default": {"cursor_name": "drag",},
    }

    def __init__(self, cell_widget: grid.CellWidget) -> None:
        super().__init__(cell_widget)
        self.my_object_id: types.MyObjectId = cell_widget.my_object.id

    def handle_move_on_grid(self, unused_event: QtGui.QDragMoveEvent) -> None:
        """
        Sets a "forbidden" cursor

        Parameters
        ----------
        unused_event

        """
        self._set_cursor_icon("forbidden", QtCore.Qt.MoveAction)

    def handle_drop_on_grid(self) -> None:
        """Nothing happens when dropping from grid to grid."""

    def handle_move_on_tree(self, unused_event: QtGui.QDragMoveEvent) -> None:
        """
        Sets the default drag cursor, or the special one if a key is being pressed.

        Parameters
        ----------
        unused_event

        """
        cursor_name = self._get_cursor_name_from_modifiers()
        self._set_cursor_icon(cursor_name, QtCore.Qt.MoveAction)

    def handle_drop_on_tree(self, widget_item_hovered: tag_tree.WidgetItem,) -> None:
        """
        Handles a drag and drop operation from the grid to the tag tree.

        If the cell being dragged is part of the current selection, the action will be
        applied to all my_objects in the selection. If not, the action will be applied
        only to the cells, even if a selection (with other cells) exists.
        The action itself is defined by the widget_item.

        Parameters
        ----------
        widget_item_hovered

        """
        if widget_item_hovered.accepts_drop:
            my_objects_dragged = self._get_my_objects_dragged()
            remove = self._needs_remove()
            for my_object_id in my_objects_dragged:
                widget_item_hovered.handle_drop_on_self(my_object_id, remove)

    @staticmethod
    def _needs_remove() -> bool:
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        needs_remove = modifiers == QtCore.Qt.ShiftModifier
        return needs_remove

    def _get_my_objects_dragged(self) -> List[types.MyObjectId]:
        selection = self._get_current_tab_selection()
        is_my_object_in_selection = self._is_my_object_in_selection(selection)
        if is_my_object_in_selection:
            my_objects_dragged = selection
        else:
            my_objects_dragged = [self.my_object_id]
        return my_objects_dragged

    def _is_my_object_in_selection(self, selection: List[types.MyObjectId]) -> bool:
        return self.my_object_id in selection

    def _get_current_tab_selection(self) -> List[types.MyObjectId]:
        current_tab = self._get_current_tab()
        selection = current_tab.selection
        return selection


class DragFromTree(MyDrag):
    """
    Drag object created from the Tag tree.

    The cursors are modified by the handle_move methods and the result of a drop by
    the handle_drop ones.

    Methods
    -------
    handle_move_on_grid
    handle_drop_on_grid
    handle_move_on_tree
    handle_drop_on_tree

    """

    _modifiers_dict = {
        QtCore.Qt.ShiftModifier: {
            "cursor_name": "minus",
            "method_name": "remove",
            "is_modifier": True,
        },
        QtCore.Qt.ControlModifier: {
            "cursor_name": "plus",
            "method_name": "add",
            "is_modifier": True,
        },
        QtCore.Qt.AltModifier: {
            "cursor_name": "filter",
            "method_name": "filter",
            "is_modifier": True,
        },
        "Default": {
            "cursor_name": "drag",
            "method_name": "base",
            "is_modifier": False,
        },
    }

    def _get_tag_tree_widget(self) -> tag_tree.TagTreeWidget:
        return self.source()

    def handle_move_on_grid(self, unused_event: QtGui.QDragMoveEvent) -> None:
        """
        Sets the default drag cursor, or the special one if a key is being pressed.

        Parameters
        ----------
        unused_event

        """
        cursor_name = self._get_cursor_name_from_modifiers()
        self._set_cursor_icon(cursor_name, QtCore.Qt.MoveAction)

    def handle_drop_on_grid(self) -> None:
        """
        Handles a drag and drop operation from the grid to the tag tree.

        If the cell being dragged is part of the current selection, the action will be
        applied to all my_objects in the selection. If not, the action will be applied
        only to the cells, even if a selection (with other cells) exists.
        The action itself is defined by the widget_item.

        """
        widget_item = self._get_widget_item()
        if not widget_item.is_droppable:
            return
        tab_widget = self._get_tab_widget()
        self._handle_drop_on_grid_depending_on_modifiers(tab_widget, widget_item)

    def _handle_drop_on_grid_depending_on_modifiers(
        self, tab_widget: grid.TabWidget, widget_item: tag_tree.WidgetItem
    ):
        need_apply_modifiers = self._get_need_apply_modifiers()
        if need_apply_modifiers:
            self._handle_drop_on_grid_with_modifiers(tab_widget, widget_item)
        else:
            self._handle_drop_on_grid_default(widget_item)

    def _handle_drop_on_grid_default(self, widget_item: tag_tree.WidgetItem) -> None:
        my_main_widget = self._get_main_widget()
        my_main_widget.add_tab_from_widget_item(widget_item)

    def _handle_drop_on_grid_with_modifiers(
        self, tab_widget: grid.TabWidget, widget_item: tag_tree.WidgetItem
    ):
        method_name = self._get_method_name_from_modifiers()
        method = getattr(tab_widget.query_parameters, method_name)
        method(widget_item.widget_item_id)
        tab_widget.refresh()

    def _get_tab_widget(self) -> grid.TabWidget:
        my_main_widget = self._get_main_widget()
        tab_widget = my_main_widget.tabs_widget.currentWidget()
        return tab_widget

    def _get_widget_item(self) -> tag_tree.WidgetItem:
        tag_tree_widget = self._get_tag_tree_widget()
        widget_item = tag_tree_widget.selectedItems()[0]
        return widget_item

    def handle_move_on_tree(self, unused_event: QtGui.QDragMoveEvent) -> None:
        """
        Sets a "forbidden" cursor

        Parameters
        ----------
        unused_event

        """
        self._set_cursor_icon("forbidden", QtCore.Qt.MoveAction)

    def handle_drop_on_tree(
        self, unused_widget_item_hovered: tag_tree.WidgetItem
    ) -> None:
        """Nothing happens when dropping from grid to grid."""
