# -*- coding: utf-8 -*-
"""Module defining the GridWidgetContainer class."""

import math
from PySide2 import QtWidgets
from .grid_widget import GridWidget
from .factory import Factory
from config.config import config
from .grid_parameters import grid_parameters


class GridWidgetContainer(QtWidgets.QWidget, Factory):

    """
    The GridWidgetContainer displays the visible part of the grid.

    When the number of cells grows, it can lead to performance issues. To display only
    a limited quantity of cells, but to keep a persistent experience of the scrollbar,
    the hidden cells above and under the visible part of the grid are replaced by
    two empty QLabels, which size are adapted whenever the scrollbar changes position.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = None
        self.grid_widget = None

    def finish_init(self):
        self.main_window = self.parent()
        self.grid_widget = GridWidget.create_widget(parent=self)
        self.layout().insertWidget(1, self.grid_widget)
        self.main_window.grid_scrollarea.verticalScrollBar().valueChanged.connect(
            self.test
        )

    def repaint(self):
        """
        Repaints the grid.

        Attributes
        ----------
        force: boolean, optional
            If true, will repaint the grid, even if redraw_grid doesn't seem necessary.

        """
        if not self.grid_widget.objects:
            # TODO : write the case where there are no objects
            # self.draw_empty_grid()
            return
        if not self.grid_widget.cells:
            self.grid_widget.create_cell(0)
        grid_parameters.cell_width = self.grid_widget.cells[0].width()
        grid_parameters.cell_height = self.grid_widget.cells[0].height()
        self.modify_width()
        self.modify_height()
        is_new_cells_displayed = self.get_cells_displayed()
        # TODO only remove and create necessary cells
        if is_new_cells_displayed:
            self.resize_hidden_containers()
            self.redraw_grid_widget()
        try:
            windows_opened = config.app.allWindows()
        except AttributeError:
            pass
        else:
            if len(windows_opened) > 1:
                print(len(windows_opened))
                for window in windows_opened:
                    try:
                        keep_open = window.title() == "MainWindow"
                    except AttributeError:
                        window.widget().close()
                    else:
                        if not keep_open:
                            window.close()

    def modify_width(self):
        columns_scrollarea = self.get_columns_scrollarea()
        self.resize_width_scrollarea(columns_scrollarea)
        grid_parameters.columns_qty = min(columns_scrollarea, grid_parameters.cells_qty)
        if grid_parameters.width != self.grid_widget.width():
            self.resize_width_grid()

    def modify_height(self):
        rows_scrollarea = self.get_rows_scrollarea()
        grid_parameters.rows_qty = math.ceil(
            grid_parameters.cells_qty / grid_parameters.columns_qty
        )
        grid_parameters.rows_displayed_qty = min(
            rows_scrollarea + 2, grid_parameters.rows_qty
        )
        if grid_parameters.height != self.grid_widget.height():
            self.resize_height_grid()

    def get_columns_scrollarea(self):
        """The number of columns that can fit in the available space for the grid."""
        window_width_new = self.main_window.width()
        scrollarea_width_available = (
            window_width_new - config.toml["tag_tree_min_width"]
        )
        grid_width_available = (
            scrollarea_width_available - config.toml["grid_horizontal_margin"]
        )
        # Having 0 column can cause bugs later in the program, so we set a
        # minimum of 1 column.
        columns_number_scrollarea = max(
            grid_width_available // grid_parameters.cell_width, 1
        )
        return columns_number_scrollarea

    def get_rows_scrollarea(self):
        """The number of rows that can fit in the available space for the grid."""
        windows_height = self.main_window.height()
        # TODO find the good value instread of tag_tree_min_width (and rename ir...)
        grid_height_available = (
            windows_height - 50  # - config.toml["grid_vertical_margin"]
        )
        rows_number_scrollarea = (
            math.ceil(grid_height_available / grid_parameters.cell_height) + 1
        )
        return rows_number_scrollarea

    def resize_width_scrollarea(self, columns_scrollarea):
        """Resizes the main_window's scroll area holding the grid."""
        scrollarea_width_new = (
            grid_parameters.cell_width * columns_scrollarea
            + config.toml["grid_horizontal_margin"]
        )
        self.main_window.grid_scrollarea.setMinimumWidth(scrollarea_width_new)
        self.main_window.grid_scrollarea.setMaximumWidth(scrollarea_width_new)

    def resize_width_grid(self):
        """Resizes the grid's width."""
        self.grid_widget.setMinimumWidth(grid_parameters.width)
        self.grid_widget.setMaximumWidth(grid_parameters.width)

    def resize_height_grid(self):
        """Resizes the grid's width."""
        self.grid_widget.setMinimumHeight(grid_parameters.height)
        self.grid_widget.setMaximumHeight(grid_parameters.height)

    def redraw_grid_widget(self):
        self.grid_widget.remove_all_cells()
        for index in range(
            grid_parameters.cell_displayed_first,
            grid_parameters.cell_displayed_last + 1,
        ):
            self.grid_widget.create_cell(index)
        self.grid_widget.repopulate_grid()
        self.grid_widget.repaint()

    def resize_hidden_containers(self):
        container_height_total = grid_parameters.rows_qty * grid_parameters.cell_height

        cells_hidden_top_quantity = (
            grid_parameters.cell_displayed_first // grid_parameters.columns_qty
        )
        self.empty_cells_top_widget.setMinimumHeight(
            cells_hidden_top_quantity * grid_parameters.cell_height
        )
        self.empty_cells_top_widget.setMaximumHeight(
            cells_hidden_top_quantity * grid_parameters.cell_height
        )

        bottom_container_height = (
            container_height_total
            - grid_parameters.height
            - self.empty_cells_top_widget.height()
        )
        self.empty_cells_bottom_widget.setMinimumHeight(bottom_container_height)
        self.empty_cells_bottom_widget.setMaximumHeight(bottom_container_height)

    # TODO remove the signal and its handling...
    def test(self):
        self.repaint()

    def get_cells_displayed(self):
        cell_displayed_first_old = grid_parameters.cell_displayed_first
        cell_displayed_last_old = grid_parameters.cell_displayed_last
        pos_y = -self.pos().y() - config.toml["grid_vertical_margin"] / 2

        grid_parameters.row_displayed_first = min(
            max(0, pos_y // grid_parameters.cell_height - 1),
            grid_parameters.rows_qty - grid_parameters.rows_displayed_qty,
        )
        grid_parameters.cell_displayed_first = int(
            grid_parameters.row_displayed_first * grid_parameters.columns_qty
        )
        grid_parameters.row_displayed_last = min(
            grid_parameters.row_displayed_first
            + grid_parameters.rows_displayed_qty
            - 1,
            grid_parameters.rows_qty,
        )
        grid_parameters.cell_displayed_last = int(
            min(
                (grid_parameters.row_displayed_last + 1) * grid_parameters.columns_qty
                - 1,
                grid_parameters.cells_qty - 1,
            )
        )

        return (
            cell_displayed_first_old != grid_parameters.cell_displayed_first
            or cell_displayed_last_old != grid_parameters.cell_displayed_last
        )
