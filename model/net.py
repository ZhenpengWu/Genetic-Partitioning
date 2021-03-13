from typing import List

from model.cell import Cell


class Net:
    def __init__(self, net_id, color) -> None:
        self.net_id = net_id
        self.cells: List[Cell] = []
        self.color = color

    def add_cell(self, cell: Cell) -> None:
        self.cells.append(cell)

    def get_source(self) -> Cell:
        """
        :return: the source, which is the first cell in the cells
        """
        return self.cells[0]

    def get_sinks(self) -> List[Cell]:
        """
        :return: the sinks, which are the cell except the first one
        """
        return self.cells[1:]
