# -*- coding: utf-8 -*-

"""
Defines :
 The TabParameters class.

 The SubWidgetParameters base class, and its derived classes GridParameters,
 GridContainerParameters and ScrollAreaParameters.

 The Limit enum, with its min and max instances.

 The CurrentParameters dataclass.

"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum

import gallery.widgets.grid as grid
import gallery.widgets.main_widget as main_widget
from gallery.config.config import Config

Pixel = int


class Limit(IntEnum):

    """Two limit types are acceptable, min and max."""

    max = 1
    min = 2


# SubWidgetParameters is the base class, and only has (shared) private methods.
class SubWidgetParameters:  # pylint: disable = too-few-public-methods.

    """
    Base class for GridParameters, GridContainerParameters and ScrollAreaParameters.
    """

    def __init__(self, tab_parameters: TabParameters) -> None:
        self._tab_parameters = tab_parameters
        self.config = tab_parameters.config

    def _get_main_widget(self) -> main_widget.MainWidget:
        tab_widget = self._tab_parameters.tab_widget
        my_main_widget = tab_widget.get_ancestor_by_class(main_widget.MainWidget)
        assert my_main_widget is not None
        return my_main_widget

    def _get_main_widget_width(self) -> Pixel:
        my_main_widget = self._get_main_widget()
        main_widget_width = my_main_widget.width()
        return main_widget_width

    def _get_main_widget_height(self) -> Pixel:
        my_main_widget = self._get_main_widget()
        main_widget_height = my_main_widget.height()
        return main_widget_height

    @staticmethod
    def _apply_limit(value: int, limit: int, min_or_max: Limit) -> int:
        if min_or_max == Limit.min:
            value_with_limit = max(value, limit)
        elif min_or_max == Limit.max:
            value_with_limit = min(value, limit)
        else:
            raise ValueError(f"{min_or_max} is not an acceptable limit type")
        return value_with_limit


class GridParameters(SubWidgetParameters):

    """
    Parameters defining the properties of the grid widget.

    The grid is the part of the tab holding the cells, and is included in the grid
    container. Its dimensions are limited by the quantity of cells to be displayed
    and are smaller than the grid container's.

    Properties
    ----------
    columns
    width
    rows
    height

    """

    @property
    def columns(self) -> int:
        """
        The number of columns in the grid.

        Can be lower than the grid container's number of columns, but cannot exceed
        the number of cells.

        """
        grid_columns = self._get_grid_container_columns()
        cells_qty = self._tab_parameters.cells_qty
        grid_columns = self._apply_limit(grid_columns, cells_qty, Limit.max)
        return grid_columns

    @property
    def width(self) -> Pixel:
        """Width of the grid."""
        cell_width = self.config.cell_width
        grid_width = self.columns * cell_width
        return grid_width

    @property
    def rows(self) -> int:
        """
        The number of rows in the grid.

        It's usually the number of rows that fit on the main widget plus one, but it
        cannot exceed the grid container's number of rows (itself based on the number
        of cells).

        """
        grid_rows = self._get_grid_rows_available()
        grid_container_rows = self._get_grid_containers_rows()
        grid_rows = self._apply_limit(grid_rows, grid_container_rows, Limit.max)
        return grid_rows

    @property
    def height(self) -> Pixel:
        """Height of the grid."""
        row_height = self.config.cell_height
        grid_height = self.rows * row_height
        return grid_height

    def _get_grid_container_columns(self) -> int:
        grid_container_parameters = self._tab_parameters.grid_container
        grid_container_columns = grid_container_parameters.columns
        return grid_container_columns

    def _get_grid_rows_available(self) -> int:
        scroll_area_height = self._get_scroll_area_height()
        row_height = self.config.cell_height
        grid_rows_available = math.ceil(scroll_area_height / row_height) + 1
        return grid_rows_available

    def _get_grid_containers_rows(self) -> int:
        grid_container_parameters = self._tab_parameters.grid_container
        grid_container_rows = grid_container_parameters.rows
        return grid_container_rows

    def _get_scroll_area_height(self) -> Pixel:
        scroll_area_parameters = self._tab_parameters.scroll_area
        scroll_area_height = scroll_area_parameters.height
        return scroll_area_height


class GridContainerParameters(SubWidgetParameters):

    """
    Parameters defining the properties of the grid container widget.

    The grid container holds the grid and the two empty containers above and below it.
    Its height corresponds to the height a grid would have if it displayed every single
    cell. For memory optimization reasons, only a limited number of cells is actually
    displayed. To keep the behaviour of the scroll bar consistent, we dynamically
    resize the two hidden containers to take the space of the hidden cells.

    Its number of columns is also dynamically adapted, and is a function of the size
    of the main window. It can be greater than the number of cells to be displayed,
    creating the illusion of "empty" columns to the right of the last cell. Its width
    is calculated to hold exactly the right number of columns. The "remaining" width
    is automatically taken by tag tree.

    Properties
    ----------
    columns
    width
    rows
    height

    """

    @property
    def columns(self) -> int:
        """The number of columns that can fit in the available space for the grid."""
        grid_width_available = self._get_grid_width_available()
        grid_container_columns = grid_width_available // self.config.cell_width
        grid_container_columns = self._apply_limit(grid_container_columns, 1, Limit.min)
        return grid_container_columns

    @property
    def width(self) -> Pixel:
        """Width of the grid container."""
        cell_width = self.config.cell_width
        grid_container_width = self.columns * cell_width
        return grid_container_width

    @property
    def rows(self) -> int:
        """
        The grid container's number of rows.

        It is equal to the number of rows that would theoretically be necessary to
        display all cells.

        """
        cells_qty = self._tab_parameters.cells_qty
        grid_container_rows = math.ceil(cells_qty / self.columns)
        return grid_container_rows

    @property
    def height(self) -> Pixel:
        """Height of the grid container."""
        row_height = self.config.cell_height
        rows_qty = self.rows
        grid_container_height = rows_qty * row_height
        return grid_container_height

    def _get_grid_width_available(self) -> Pixel:
        scroll_area_parameters = self._tab_parameters.scroll_area
        scroll_area_width_available = scroll_area_parameters.width_available
        grid_width_available = scroll_area_width_available - self.config.scrollbar_width
        return grid_width_available


class ScrollAreaParameters(SubWidgetParameters):

    """
    Parameters defining the properties of the scroll area.

    The width is dynamically calculated so as to fit a whole number of columns, while
    keeping a minimum width for the tag tree. Its height is simply based on the
    main widget's one, minus the space for the borders.

    Properties
    ----------
    width_available
    width
    height

    """

    @property
    def width_available(self) -> Pixel:
        """The width available in which to draw the scroll area."""
        main_widget_width = self._get_main_widget_width()
        width_available = main_widget_width - self.config.tag_tree_min_width
        return width_available

    @property
    def width(self) -> Pixel:
        """The actual width, calculated to fit a whole number of columns."""
        grid_container_parameters = self._tab_parameters.grid_container
        grid_container_width = grid_container_parameters.width
        scroll_area_width = grid_container_width + self.config.scrollbar_width
        return scroll_area_width

    @property
    def height(self) -> Pixel:
        """Height of the scroll area."""
        main_widget_height = self._get_main_widget_height()
        scroll_area_height = main_widget_height - self.config.grid_vertical_margin
        return scroll_area_height


class TabParameters:

    """
    Parameters defining the properties of the tab widget.

    The TabParameters also holds the properties for its subwidgets in appropriate
    attributes, and the last values used in CurrentParameters, in order to
    determine whether something has changed and should be updated.

    Properties
    ----------
    tab_widget
    scroll_area
    grid_container
    grid
    current_parameters

    """

    def __init__(self, tab_widget: grid.TabWidget) -> None:
        self.tab_widget: grid.TabWidget = tab_widget
        self.scroll_area: ScrollAreaParameters = ScrollAreaParameters(self)
        self.grid_container: GridContainerParameters = GridContainerParameters(self)
        self.grid: GridParameters = GridParameters(self)
        self.current_parameters: CurrentParameters = CurrentParameters()

    @property
    def config(self) -> Config:
        """The Config of the TabWidget, shared with the subwidgets' parameters."""
        return self.tab_widget.config

    @property
    def cells_qty(self):
        """The total number of cells to be displayed."""
        objects = self.tab_widget.get_my_objects_list()
        return len(objects)

    @property
    def width(self) -> Pixel:
        """Width of the TabWidget."""
        return self.scroll_area.width + 9

    def get_cells_displayed_first(self) -> int:
        """The first cell to be displayed."""
        rows_displayed_first = self.get_rows_displayed_first()
        columns = self.grid_container.columns
        cells_displayed_first = rows_displayed_first * columns
        return cells_displayed_first

    def get_rows_displayed_first(self) -> int:
        """The first row to be displayed."""
        grid_widget_vertical_position = (
            self._get_grid_widget_vertical_position()
        )
        rows_displayed_first = (
            grid_widget_vertical_position // self.config.cell_height
        )
        rows_displayed_first = self._apply_rows_displayed_first_limits(
            rows_displayed_first)
        return int(rows_displayed_first)

    def _apply_rows_displayed_first_limits(self, rows_displayed_first: int) -> int:
        rows_displayed_first = self._apply_rows_displayed_first_limit_min(
            rows_displayed_first)
        rows_displayed_first = self._apply_rows_displayed_first_limit_max(
            rows_displayed_first)
        return rows_displayed_first

    def _apply_rows_displayed_first_limit_max(self, rows_displayed_first: int) -> int:
        limit_max = self.grid_container.rows - self.grid.rows
        rows_displayed_first = min(rows_displayed_first, limit_max)
        return rows_displayed_first

    @staticmethod
    def _apply_rows_displayed_first_limit_min(rows_displayed_first: int) -> int:
        limit_min = 0
        rows_displayed_first = max(rows_displayed_first, limit_min)
        return rows_displayed_first

    def _get_grid_widget_vertical_position(self) -> Pixel:
        grid_widget_container = self.tab_widget.grid_widget_container
        grid_widget_vertical_position = -grid_widget_container.pos().y()
        return grid_widget_vertical_position

    def get_cells_displayed_last(self) -> int:
        """The last cell to be displayed."""
        cells_hidden_first = self._get_cells_hidden_first()
        cells_displayed_last = cells_hidden_first - 1
        cells_displayed_last = self._apply_cells_displayed_last_limit(
            cells_displayed_last)
        return cells_displayed_last

    def _apply_cells_displayed_last_limit(self, cells_displayed_last: int) -> int:
        limit_max = self.cells_qty - 1
        cells_displayed_last = min(cells_displayed_last, limit_max)
        return cells_displayed_last

    def _get_cells_hidden_first(self) -> int:
        rows_hidden_first = self._get_rows_hidden_first()
        grid_container_columns = self.grid_container.columns
        cell_hidden_first = rows_hidden_first * grid_container_columns
        return cell_hidden_first

    def _get_rows_hidden_first(self) -> int:
        rows_displayed_first = self.get_rows_displayed_first()
        grid_rows = self.grid.rows
        rows_hidden_first = rows_displayed_first + grid_rows
        return rows_hidden_first

    def need_redraw_cells(self) -> bool:
        """Whether or not we need to redraw the cells."""
        has_changed_cells_displayed = self._has_changed_cells_displayed()
        has_changed_grid_columns = self._has_changed_grid_columns()
        return has_changed_cells_displayed or has_changed_grid_columns

    def _has_changed_cells_displayed(self) -> bool:
        has_changed_cells_displayed_first = self._has_changed_cells_displayed_first()
        has_changed_cells_displayed_last = self._has_changed_cells_displayed_last()
        return has_changed_cells_displayed_first or has_changed_cells_displayed_last

    def _has_changed_cells_displayed_first(self) -> bool:
        new_cells_displayed_first = self.get_cells_displayed_first()
        old_cells_displayed_first = self.current_parameters.cells_displayed_first
        return new_cells_displayed_first != old_cells_displayed_first

    def _has_changed_cells_displayed_last(self) -> bool:
        new_cells_displayed_last = self.get_cells_displayed_last()
        old_cells_displayed_last = self.current_parameters.cells_displayed_last
        return new_cells_displayed_last != old_cells_displayed_last

    def _has_changed_grid_columns(self) -> bool:
        new_grid_columns = self.grid.columns
        old_grid_columns = self.current_parameters.grid_columns
        return new_grid_columns != old_grid_columns

    def update_current_parameters(self) -> None:
        """Reset the current parameters."""
        self._update_cells_displayed()
        self._update_grid_columns()
        self._update_grid_container_columns()

    def _update_cells_displayed(self) -> None:
        self.current_parameters.cells_displayed_first = self.get_cells_displayed_first()
        self.current_parameters.cells_displayed_last = self.get_cells_displayed_last()

    def _update_grid_columns(self) -> None:
        self.current_parameters.grid_columns = self.grid.columns

    def _update_grid_container_columns(self) -> None:
        self.current_parameters.grid_container_width = self.grid_container.width

    def need_resize_grid_container_width(self):
        """Whether or not the grid container width has changed."""
        # This method is only used in the case where the grid container width is
        # modified but not the grid itself, which can happen if there aren't enough
        # cells to fill a single row.
        old_grid_container_width = self.current_parameters.grid_container_width
        new_grid_container_width = self.grid_container.width
        return old_grid_container_width != new_grid_container_width


@dataclass()
class CurrentParameters:

    """Parameters used since the last time the TabWidget was drawn."""

    cells_displayed_first = 0
    cells_displayed_last = 0
    grid_columns = 0
    grid_container_width = 0
