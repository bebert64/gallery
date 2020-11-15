from dataclasses import dataclass


@dataclass
class GridParameters:
    columns_qty: int = 0
    rows_qty: int = 0
    cells_qty: int = 0
    cell_width: int = 0
    cell_height: int = 0
    cell_displayed_first: int = 0
    cell_displayed_last: int = 0
    rows_displayed_qty: int = 0
    row_displayed_first: int = 0
    row_displayed_last: int = 0

    @property
    def width(self):
        return self.cell_width * self.columns_qty

    @property
    def height(self):
        return self.cell_height * self.rows_displayed_qty


grid_parameters = GridParameters()
