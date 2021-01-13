# -*- coding: utf-8 -*-

"""
Defines :
 The CellWidget class, and its associated CellSignals.

 The TabWidget class, and its associated TabSignals.

"""

from __future__ import annotations

import operator
from typing import List, Callable, Tuple

from PySide6 import QtWidgets, QtCore, QtGui

import gallery.types as types
import gallery.widgets.drag as drag
import gallery.widgets.main_widget as main_widget
from gallery.widgets.my_custom_widget import MyCustomWidget
from gallery.widgets.query import QueryParameters
from gallery.widgets.widget_parameters import TabParameters


class CellWidget(QtWidgets.QWidget, MyCustomWidget):

    """
    A single cell in the gallery, representing a user-defined my_object (later referenced
    as my_object).

    If the my_object has a thumbnail_path method, it will be used to give the cell the
    path to a thumbnail image, displayed on the cell background. The cell widget also
    has a transparent overlay which can be hidden or shown, to indicate whether
    the cell is selected.

    Attributes
    ----------
    my_object
    signals
    overlay
    position_at_click: QPoint

    Class Method
    ------------
    create_cell_widget

    Warning
    -------
    The CellWidget should not be instantiated directly, but one should rather use
    the create_cell_widget factory method.

    """

    def __init__(self, parent: TabWidget) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.my_object: types.MyObjectType
        self.signals: CellSignals = CellSignals(self)
        self.overlay: QtWidgets.QLabel
        self.position_at_click: QtCore.QPoint
        """Coordinates of the mouse at the moment it is clicked."""
        # self.my_popup: QtWidgets.QWidget = None

    @classmethod
    def create_cell_widget(
        cls,
        parent: TabWidget,
        my_object: types.MyObjectType,
        handle_cell_clicked: Callable,
    ) -> CellWidget:
        """
        Factory method to create cell widgets.

        Parameters
        ----------
        parent
        my_object
        handle_cell_clicked

        """
        # create_cell_widget is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        cell_widget = cls.create_widget(parent)
        assert isinstance(cell_widget, CellWidget)
        cell_widget.my_object = my_object
        cell_widget._init_graphical_aspects()
        cell_widget.signals.clicked.connect(handle_cell_clicked)  # type: ignore
        # cell_widget._set_mouse_tracking_on_self_and_children()
        return cell_widget

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.deleteLater()
        super().closeEvent(event)

    def _init_graphical_aspects(self) -> None:
        cell_width, cell_height = self.config.cell_width, self.config.cell_height
        self.setFixedSize(cell_width, cell_height)
        self._add_overlay()
        self._add_image()

    # def _set_mouse_tracking_on_self_and_children(self) -> None:
    #     self.setMouseTracking(True)
    #     for child in self.findChildren(QtCore.QObject):
    #         try:
    #             child.setMouseTracking(True)
    #         except AttributeError:
    #             pass

    def _add_overlay(self) -> None:
        self.overlay = QtWidgets.QLabel(self)
        self.overlay.setStyleSheet(
            f"background-color: {self.config.cell_overlay_color};"
        )
        self.overlay.setFixedSize(self.size())
        self.overlay.hide()

    def _add_image(self) -> None:
        has_thumbnail = self._has_thumbnail()
        if has_thumbnail:
            self._set_background_image()
        else:
            self._set_default_label()

    def _set_default_label(self) -> None:
        label_text = self._get_default_label_text()
        self.label.setText(label_text)

    def _get_default_label_text(self) -> str:
        has_object_name = hasattr(self.my_object, "name")
        if has_object_name:
            label_text = self.my_object.name
        else:
            label_text = str(self.my_object.id)
        return label_text

    def _set_background_image(self) -> None:
        background_image_scaled = self._get_background_image_scaled()
        self.label.setPixmap(background_image_scaled)
        self.label.setScaledContents(False)

    def _get_background_image_scaled(self) -> QtGui.QPixmap:
        background_image = self._get_background_image()
        background_image_scaled = background_image.scaled(
            self.config.cell_width, self.config.cell_height, QtCore.Qt.KeepAspectRatio,
        )
        return background_image_scaled

    def _get_background_image(self) -> QtGui.QPixmap:
        thumbnail_path = self.my_object.thumbnail_path()
        background_image = QtGui.QPixmap(str(thumbnail_path))
        return background_image

    def _has_thumbnail(self) -> bool:
        if hasattr(self.my_object, "thumbnail_path"):
            thumbnail_path = self.my_object.thumbnail_path()
            has_thumbnail = thumbnail_path.exists()
        else:
            has_thumbnail = False
        return has_thumbnail

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.position_at_click = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # if self.my_popup is not None:
        #     self.my_popup.setParent(None)
        #     self.my_popup = None
        # buttons = event.buttons()
        # print(f"{(event.buttons() == QtCore.Qt.LeftButton)=}")
        # print(f"{event.modifiers()=}")
        need_start_drag = self._need_start_drag(event)
        if need_start_drag:
            my_drag = drag.DragFromGrid(self)
            my_drag.exec_()

    def _need_start_drag(self, event: QtGui.QMouseEvent) -> bool:
        if event.buttons() != QtCore.Qt.LeftButton:
            need_start_drag = False
        else:
            need_start_drag = self._is_drag_distance_enough(event)
        return need_start_drag

    def _is_drag_distance_enough(self, event: QtGui.QMouseEvent) -> bool:
        drag_distance = (event.pos() - self.position_at_click).manhattanLength()
        min_drag_distance = self.config.cell_min_drag_distance
        need_start_drag = drag_distance >= min_drag_distance
        return need_start_drag

    # def display_popup(self) -> None:
    #     return

    # def enterEvent(self, event: QtGui.QEnterEvent) -> None:
    #     self.hovered = True
    #     super().enterEvent(event)

    # def leaveEvent(self, event):  #: QtGui.QLeaveEvent) -> None:
    #     self.hovered = False
    #     # if self.my_popup is not None:
    #     #     self.my_popup.setParent(None)
    #     #     self.my_popup = None
    #     super().leaveEvent(event)

    # def _is_hovered(self) -> bool:
    #     """Check if the cell is currently being hovered."""
    #     tab_widget = self.get_ancestor_by_class(TabWidget)
    #     if tab_widget is None:
    #         return False
    #     return self == tab_widget.cell_hovered()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            if self.position_at_click == event.pos():
                self.signals.clicked.emit()  # type: ignore
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, unused_event: QtGui.QMouseEvent) -> None:
        if hasattr(self.my_object, "action_double_click"):
            self.my_object.action_double_click()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu(self)
        self._add_actions_to_context_menu(menu)
        menu_position = self.mapToGlobal(event.pos())
        menu.exec_(menu_position)

    def _add_actions_to_context_menu(self, menu: QtWidgets.QMenu) -> None:
        if hasattr(self.my_object, "actions"):
            for name, func in self.my_object.actions:
                menu.addAction(name).triggered.connect(func)


class CellSignals(QtCore.QObject):  # pylint: disable=too-few-public-methods

    # Only a QObject can hold signals, which is why we need a QObject subclass as an
    # intermediate attribute of the QWidget to which we want to attach those signals.
    # By QT design, the signal also needs to be a class instance of the my_object, so
    # I haven't found a cleaner way than to create a class holding only that signals...

    """
    Collection of signals used by the CellWidget.

    Parameters
    ----------
    cell

    Attributes
    ----------
    clicked
        A signal emitted when the cell is clicked.

    """

    clicked: QtCore.Signal = QtCore.Signal()

    def __init__(self, cell: CellWidget):
        super().__init__()
        self.cell: CellWidget = cell


class TabWidget(QtWidgets.QWidget, MyCustomWidget):

    """
    A tab to be displayed on the right hand side of the Main Widget.

    The tabs holds a grid, which my_objects are defined by query parameters.

    Attributes
    ----------
    my_objects
    cells
    selection
    query_parameters
    tab_parameters
    signals

    Class methods
    -------------
    create_tab_widget

    Warning
    -------
    The CellWidget should not be instantiated directly, but one should rather use
    the create_cell_widget factory method.

    """

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.cells: List[CellWidget] = []
        self.selection: List[types.MyObjectId] = []
        self.query_parameters: QueryParameters
        self.tab_parameters: TabParameters
        self.signals: TabSignals = TabSignals()

    @classmethod
    def create_tab_widget(
        cls, parent: QtWidgets.QWidget, query_parameters: QueryParameters
    ) -> TabWidget:
        """
        Factory method to create tab widgets.

        Parameters
        ----------
        parent
        query_parameters

        """
        # create_tab_widget is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        tab_widget = super().create_widget(parent)
        assert isinstance(tab_widget, TabWidget)
        tab_widget.tab_parameters = TabParameters(tab_widget)
        tab_widget.query_parameters = query_parameters
        tab_widget.scroll_area.verticalScrollBar().valueChanged.connect(
            tab_widget._draw_grid_non_empty
        )
        return tab_widget

    def refresh(self) -> None:
        """Refreshes a tab and the main_widget status bar."""
        self._refresh_my_objects()
        self._refresh_selection()
        self.redraw()
        # The signal is picked_up by the main_widget and is used to refresh the
        # status bar.
        self.signals.my_objects_modified.emit()  # type: ignore

    def _refresh_my_objects(self) -> None:
        self.query_parameters.refresh_my_objects()

    def _refresh_selection(self) -> None:
        self.selection = []

    def get_my_objects_list(self) -> List[types.MyObjectType]:
        """The list of objects associated with the tab's query parameters."""
        my_objects_set = self.query_parameters.my_objects
        my_objects_list = list(my_objects_set)
        my_objects_list_sorted = sorted(my_objects_list, key=operator.attrgetter("id"))
        return my_objects_list_sorted

    def _get_main_widget(self):
        return self.get_ancestor_by_class(main_widget.MainWidget)

    def _get_drag_object(self) -> drag.MyDrag:
        my_main_widget = self._get_main_widget()
        drag_object = my_main_widget.drag_object
        return drag_object

    def dragEnterEvent(  # pylint: disable=no-self-use
        self, event: QtGui.QDragEnterEvent
    ) -> None:
        event.accept()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        drag_object = self._get_drag_object()
        drag_object.handle_move_on_grid(event)

    def dropEvent(self, unused_event: QtGui.QDropEvent) -> None:
        drag_object = self._get_drag_object()
        drag_object.handle_drop_on_grid()

    def redraw(self) -> None:
        """Repaints the grid."""
        is_grid_empty = self._is_grid_empty()
        if is_grid_empty:
            self._draw_grid_empty()
        else:
            self._draw_grid_non_empty()

    def _draw_grid_non_empty(self) -> None:
        self._resize_height()
        # _redraw_grid_widget is a more general case, and includes a call to
        # _resize_width
        if self._need_redraw_grid_widget():
            self._redraw_grid_widget()
        elif self._need_resize_grid_widget_container_width():
            self._resize_width()

    def _need_resize_grid_widget_container_width(self) -> bool:
        return self.tab_parameters.need_resize_grid_container_width()

    def _update_query_parameters_has_changed(self) -> None:
        self.query_parameters.reset_has_changed_attribute()

    def _update_tab_parameters(self) -> None:
        self.tab_parameters.update_current_parameters()

    def _is_grid_empty(self) -> bool:
        return len(self.get_my_objects_list()) == 0

    def _need_redraw_grid_widget(self) -> bool:
        need_from_tab_parameter = self.tab_parameters.need_redraw_cells()
        need_from_query = self.query_parameters.has_changed
        return need_from_tab_parameter or need_from_query

    def _draw_grid_empty(self) -> None:
        self._remove_all_cells()
        self._resize_height()
        self.empty_cells_top_widget.setFixedSize(0, 0)

    def _resize_width(self) -> None:
        self._resize_all_widgets_width()
        self._update_tab_parameters()

    def _resize_all_widgets_width(self) -> None:
        self._resize_grid_widget_width()
        self._resize_grid_widget_container_width()
        self._resize_scroll_area_width()
        self._resize_tab_widget_width()

    def _resize_tab_widget_width(self) -> None:
        tabs_container = self._get_main_widget().tabs_widget
        tab_widget_width = self.tab_parameters.width
        tabs_container.setFixedWidth(tab_widget_width)

    def _resize_scroll_area_width(self) -> None:
        scroll_area_width = self.tab_parameters.scroll_area.width
        self.scroll_area.setFixedWidth(scroll_area_width)

    def _resize_grid_widget_container_width(self) -> None:
        grid_widget_container_width = self.tab_parameters.grid_container.width
        self.grid_widget_container.setFixedWidth(grid_widget_container_width)

    def _resize_grid_widget_width(self) -> None:
        grid_widget_width = self.tab_parameters.grid.width
        self.grid_widget.setFixedWidth(grid_widget_width)

    def _resize_height(self) -> None:
        self._resize_grid_widget_height()
        self._resize_grid_widget_container_height()
        self._resize_hidden_containers()

    def _resize_grid_widget_container_height(self) -> None:
        grid_container_height = self.tab_parameters.grid_container.height
        self.grid_widget_container.setFixedHeight(grid_container_height)

    def _resize_grid_widget_height(self) -> None:
        grid_height = self.tab_parameters.grid.height
        self.grid_widget.setFixedHeight(grid_height)

    def _redraw_grid_widget(self) -> None:
        self._remove_all_cells()
        self._repopulate_grid()
        self._resize_width()
        self._update_query_parameters_has_changed()

    def _resize_hidden_containers(self) -> None:
        empty_cells_top_widget_height = self._get_empty_cells_top_widget_height()
        self._resize_empty_cells_top_widget(empty_cells_top_widget_height)
        self._resize_empty_cells_bottom_widget(empty_cells_top_widget_height)

    def _resize_empty_cells_bottom_widget(
        self, empty_cells_top_widget_height: int
    ) -> None:
        empty_cells_bottom_height = (
            self.tab_parameters.grid_container.height
            - self.tab_parameters.grid.height
            - empty_cells_top_widget_height
        )
        self.empty_cells_bottom_widget.setFixedHeight(empty_cells_bottom_height)

    def _resize_empty_cells_top_widget(
        self, empty_cells_top_widget_height: int
    ) -> None:
        self.empty_cells_top_widget.setFixedHeight(empty_cells_top_widget_height)

    def _get_empty_cells_top_widget_height(self) -> int:
        rows_hidden_top = self.tab_parameters.get_rows_displayed_first()
        row_height = self.config.cell_height
        empty_cells_top_widget_height = rows_hidden_top * row_height
        return empty_cells_top_widget_height

    def _create_cell(self, cell_index: int) -> CellWidget:
        my_object = self._get_my_object(cell_index)
        cell = CellWidget.create_cell_widget(self, my_object, self._handle_cell_clicked)
        self._handle_is_cell_selected(cell)
        return cell

    def _handle_is_cell_selected(self, cell: CellWidget) -> None:
        if cell.my_object.id in self.selection:
            cell.overlay.show()

    def _get_my_object(self, my_object_index: int) -> types.MyObjectType:
        my_objects = self.get_my_objects_list()
        my_object = my_objects[my_object_index]
        return my_object

    def _repopulate_grid(self) -> None:
        grid_layout = self.grid_layout
        row, column = 0, 0
        cell_range = self._get_cell_range()
        for cell_index in cell_range:
            self._add_cell_to_grid_layout(grid_layout, cell_index, row, column)
            row, column = self._move_to_next_cell(row, column)

    def _add_cell_to_grid_layout(
        self, grid_layout: QtWidgets.QGridLayout, cell_index: int, row: int, column: int
    ) -> None:
        cell = self._create_cell(cell_index)
        grid_layout.addWidget(cell, row, column)
        self.cells.append(cell)

    def _move_to_next_cell(self, row: int, column: int) -> Tuple[int, int]:
        if column == self.tab_parameters.grid_container.columns - 1:
            column = 0
            row += 1
        else:
            column += 1
        return row, column

    def _get_cell_range(self) -> range:
        cell_range = range(
            self.tab_parameters.get_cells_displayed_first(),
            self.tab_parameters.get_cells_displayed_last() + 1,
        )
        return cell_range

    def _remove_all_cells(self) -> None:
        grid_widget = self.grid_widget
        self._close_all_grid_children(grid_widget)
        self.cells = []

    @staticmethod
    def _close_all_grid_children(grid_widget: QtWidgets.QWidget) -> None:
        for child in grid_widget.children():
            if isinstance(child, CellWidget):
                child.close()

    def _handle_cell_clicked(self) -> None:
        cell = self.sender().cell
        my_object_id = cell.my_object.id
        if self._need_modify_selection():
            self._modify_selection(cell, my_object_id)
        else:
            self._create_new_selection(cell, my_object_id)

    @staticmethod
    def _need_modify_selection() -> bool:
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        need_modify_selection = modifiers == QtCore.Qt.ControlModifier
        return need_modify_selection

    def _create_new_selection(
        self, selected_cell: CellWidget, my_object_id: types.MyObjectId
    ) -> None:
        self.selection = [my_object_id]
        for cell in self.cells:
            cell.overlay.hide()
        selected_cell.overlay.show()

    def _modify_selection(
        self, cell: CellWidget, my_object_id: types.MyObjectId
    ) -> None:
        if my_object_id in self.selection:
            self._remove_cell_from_selection(cell, my_object_id)
        else:
            self._add_cell_to_selection(cell, my_object_id)

    def _add_cell_to_selection(
        self, cell: CellWidget, my_object_id: types.MyObjectId
    ) -> None:
        self.selection.append(my_object_id)
        cell.overlay.show()

    def _remove_cell_from_selection(
        self, cell: CellWidget, my_object_id: types.MyObjectId
    ) -> None:
        self.selection.remove(my_object_id)
        cell.overlay.hide()

    # def cell_hovered(self) -> Optional[CellWidget]:
    #     """The cell being hovered, or None if none are hovered."""
    #     cursor = QtGui.QCursor()
    #     # For some weird reason, mypy gets the pos() signature wrong...
    #     pos = cursor.pos()  # type: ignore
    #     for cell in self.cells:
    #         relative_pos = cell.mapFromGlobal(pos)
    #         if cell.rect().contains(relative_pos):
    #             return cell
    #     return None


class TabSignals(QtCore.QObject):  # pylint: disable=too-few-public-methods

    # Only a QObject can hold signals, which is why we need a QObject subclass as an
    # intermediate attribute of the QWidget to which we want to attach those signals.
    # By QT design, the signal also needs to be a class instance of the my_object, so
    # I haven't found a cleaner way than to create a class holding only that signals...

    """
    Collection of signals used by the TabWidget.

    Attributes
    ----------
    my_objects_modified: QtCore.Signal
        A signal emitted when the collection of my_objects is modified.

    """

    my_objects_modified: QtCore.Signal = QtCore.Signal()
