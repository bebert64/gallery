# -*- coding: utf-8 -*-

"""
Defines :
 The MainWidget class.

 The add_cell_dimension_menu convenience method, allowing to add a menu with options
 to modify the cell dimensions to a main_window which has a main_widget attribute.

"""

from __future__ import annotations

from typing import List, Dict, Optional

import peewee
from PySide6 import QtWidgets, QtGui

import gallery.types as types
from gallery.config.config import Config, CellDimension
from gallery.models.views import View
from gallery.widgets.drag import MyDrag
from gallery.widgets.grid import TabWidget
from gallery.widgets.my_custom_widget import MyCustomWidget
from gallery.widgets.query import QueryParameters
from gallery.widgets.tag_tree import (
    TagTreeWidget,
    WidgetItem,
    WidgetItemView,
)

KEYS: Dict[str, int] = {
    "CTRL": 16777249,
    "S": 83,
    "F5": 16777268,
}
"""A dictionary mapping description to their code as :class:`QKeyPressed` event."""


class MainWidget(QtWidgets.QWidget, MyCustomWidget):
    """
    The main widget to create, composed of the tag tree on the left, and a tab widget
    on the right, with each tab containing a grid of objects.

    Attributes
    ----------
    tag_tree_widget
    tabs_widget
    config
    drag_object

    Methods
    -------
    create_main_widget

    Attention
    ---------
    This widget should not be instantiated directly, but rather through the factory
    method create_main_widget.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_tree_widget: TagTreeWidget
        self.tabs_widget: QtWidgets.QTabWidget
        self.config: Config
        self.drag_object: Optional[MyDrag] = None
        self._key_pressed: List[int] = []

    @classmethod
    def create_main_widget(
        cls,
        parent,
        database: peewee.SqliteDatabase,
        MyObject: types.MyObjectType,
        options=None,
    ) -> MainWidget:
        """
        Factory method to create a main widget.

        Parameters
        ----------
        parent
        database
        MyObject
        options

        """
        # create_main_widget is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        main_widget = super().create_widget(parent)
        assert isinstance(main_widget, MainWidget)
        main_widget.config = Config(database, MyObject, options)
        main_widget._add_subwidgets()
        main_widget.update_status_bar()
        return main_widget

    def _add_subwidgets(self):
        self._add_tag_tree_widget()
        self._init_tabs_widget()

    def _init_tabs_widget(self) -> None:
        self.tabs_widget.tabCloseRequested.connect(self._close_tab)
        self.tabs_widget.currentChanged.connect(self._handle_tab_change)
        self._add_tabs()

    def _close_tab(self, tab_index: int) -> None:
        # If there is only one tab left, a new tab with all objects will be created
        # before actually closing the old one, so that there is always at least one
        # tab opened.
        if self.tabs_widget.count() == 1:
            widget_item_all = self.tag_tree_widget.widget_items["all"]
            self.add_tab_from_widget_item(widget_item_all)
        self.tabs_widget.removeTab(tab_index)

    def _handle_tab_change(self, unused_tab_index: int) -> None:
        self._refresh_current_tab()
        self.update_status_bar()

    def _add_tabs(self) -> None:
        self.add_tab_from_widget_item(self.tag_tree_widget.widget_items["all"])

    def _add_tab_from_view(self, view: View) -> None:
        widget_item_id = WidgetItemView.get_id(view)
        widget_item = self.tag_tree_widget.widget_items[widget_item_id]
        self.add_tab_from_widget_item(widget_item)

    def add_tab_from_widget_item(self, widget_item: WidgetItem) -> None:
        """Creates a tab based on the widget item and add it to the tabs_widget."""
        tab_widget = self._create_tab_from_widget_item(widget_item)
        self.tabs_widget.addTab(tab_widget, widget_item.name)
        self.tabs_widget.setCurrentWidget(tab_widget)

    def _create_tab_from_widget_item(self, widget_item: WidgetItem) -> TabWidget:
        query_parameters = QueryParameters.create_from_widget_item(widget_item)
        tab_widget = TabWidget.create_tab_widget(self, query_parameters)
        tab_widget.name = widget_item.name
        tab_widget.signals.my_objects_modified.connect(  # type: ignore
            self.update_status_bar
        )
        return tab_widget

    def _add_tag_tree_widget(self) -> None:
        self.tag_tree_widget = TagTreeWidget.create_tag_tree_widget(self)
        self.tree_and_grid_container.layout().insertWidget(0, self.tag_tree_widget)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.tabs_widget.currentWidget().redraw()
        super().resizeEvent(event)

    def _clear_status_bar(self) -> None:
        status_bar = self._get_status_bar()
        if status_bar is not None:
            self._close_children_recursively(status_bar)

    def _close_children_recursively(self, parent: QtWidgets.QWidget) -> None:
        for widget in parent.children():
            is_widget_closable = hasattr(widget, "close")
            if is_widget_closable:
                widget.close()
            else:
                self._close_children_recursively(widget)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self._key_pressed.append(event.key())
        if event.key() == KEYS["F5"]:
            self._refresh_current_tab()
        if all(key in self._key_pressed for key in [KEYS["CTRL"], KEYS["S"]]):
            print("saving")

    def _refresh_current_tab(self) -> None:
        current_tab: TabWidget = self.tabs_widget.currentWidget()
        current_tab.refresh()

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        try:
            self._key_pressed.remove(event.key())
        except ValueError:
            print(event.key())

    def save_view(self) -> None:
        """Saves the current view in the database."""
        view = self._create_view()
        view.save()
        self.tag_tree_widget.redraw_tree()

    def _create_view(self) -> View:
        current_tab = self.tabs_widget.currentWidget()
        view = self.config.models.MyView(name=current_tab.name)
        query_parameters = current_tab.query_parameters
        view.query_string = query_parameters.get_query_string()
        return view

    def update_status_bar(self) -> None:
        """Displays the current query and the number of objects in the status bar."""
        has_main_window_status_bar = self._has_main_window_status_bar()
        if has_main_window_status_bar:
            self._update_status_bar()

    def _get_status_bar(self) -> Optional[QtWidgets.QStatusBar]:
        main_window = self.get_main_window()
        if main_window is not None:
            status_bar = main_window.status_bar
        else:
            status_bar = None
        return status_bar

    def _update_status_bar(self) -> None:
        self._clear_status_bar()
        status_bar = self._get_status_bar()
        if status_bar is not None:
            self._set_status_bar_message(status_bar)

    def _set_status_bar_message(self, status_bar: QtWidgets.QStatusBar) -> None:
        message = self._get_status_bar_message()
        widget = QtWidgets.QPushButton(message, status_bar)
        status_bar.addWidget(widget)

    def _has_main_window_status_bar(self) -> bool:
        return hasattr(self.get_main_window(), "status_bar")

    def _get_status_bar_message(self) -> str:
        current_tab = self.tabs_widget.currentWidget()
        query_parameters = current_tab.query_parameters
        query_as_string = str(query_parameters)
        results = len(query_parameters.my_objects)
        return f"{query_as_string} : {results}"

    def modify_cell_zoom(self, cell_dimension: CellDimension) -> None:
        """
        Hook method to change the cell dimension.

        Parameters
        ----------
        cell_dimension

        """
        self.config.change_cell_dimension(cell_dimension)
        self._refresh_current_tab()


def add_cell_dimension_menu(main_window: QtWidgets.QMainWindow) -> None:
    """Convenience method to add a menu to a MainWindow with the cell dimensions."""
    assert hasattr(main_window, "main_widget")
    menu_folder = _create_menu_folder(main_window, "Cellules")
    for cell_dimension in CellDimension:
        _create_and_connect_cell_dimension_action(
            menu_folder, cell_dimension, main_window
        )


def _create_menu_folder(
    main_window: QtWidgets.QMainWindow, menu_name: str
) -> QtWidgets.QMenu:
    menu_bar = main_window.menuBar()
    menu_folder = menu_bar.addMenu(menu_name)
    return menu_folder


def _create_and_connect_cell_dimension_action(
    menu_folder: QtWidgets.QMenu,
    cell_dimension: CellDimension,
    main_window: QtWidgets.QMainWindow,
) -> None:
    action_name = f"{cell_dimension.name} cells"
    new_action = QtGui.QAction(action_name, main_window)
    main_widget: MainWidget = main_window.main_widget
    new_action.triggered.connect(lambda: main_widget.modify_cell_zoom(cell_dimension))  # pylint: disable=no-member
    menu_folder.addAction(new_action)
