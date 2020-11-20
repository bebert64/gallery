# -*- coding: utf-8 -*-
"""
Module containg definition for the GridParameters.

Defines a GridParameters class, containing all graphical information needed by various
widget to draw or define themselves.

Creates an instance, "grid_parameters", that can be share by all modules from the
application.

"""

from dataclasses import dataclass


@dataclass
class GridParameters:
    """
    The GridParameters calss allows to share parameters between the GridWidget and
    the GridWidgetContainer.

    Attributes
    ----------
    columns_qty: int
        The number of columns displayed. Default is 0.
    rows_qty: int
        The number of rows displayed. Default is 0.
    cells_qty: int
        The total number of cells potentially present (but not necessarily displayed).
        Default is 0.
    cell_width: int
        The with of a single cell. Default is 0.
    cell_height: int
        The height of a single cell. Default is 0.
    cell_displayed_first: int
        The first cell to be displayed. Default is 0.
    cell_displayed_last: int
        The last cell to be displayed. Default is 0.
    rows_displayed_qty: int
        The number of rows displayed. Default is 0.
    row_displayed_first: int
        The first row displayed. Default is 0.
    row_displayed_last: int
        The last row displayed. Default is 0.

    """

    columns_qty = 0
    rows_qty = 0
    cells_qty = 0
    cell_width = 0
    cell_height = 0
    cell_displayed_first = 0
    cell_displayed_last = 0
    rows_displayed_qty = 0
    row_displayed_first = 0
    row_displayed_last = 0

    @property
    def width(self):
        """The total width displayed."""
        return self.cell_width * self.columns_qty

    @property
    def height(self):
        """The total height displayed."""
        return self.cell_height * self.rows_displayed_qty


grid_parameters = GridParameters()
