from typing import List

from model.cell import Cell


class Net:
    def __init__(self, nid, color) -> None:
        self.net_id = nid
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

    # def move_node(self, result, F, T):
    #     if result.nets_distribution[self.net_id][T] == 0:
    #         for nei in self.cells:
    #             if nei.is_unlocked():
    #                 nei.adjust_gain(result.blocks, 1)
    #     elif result.nets_distribution[self.net_id][T] == 1:
    #         for nei in self.cells:
    #             if nei.is_unlocked() and nei.block_id == T:
    #                 nei.adjust_gain(result.blocks, -1)
    #
    #     result.nets_distribution[self.net_id][F] -= 1
    #     result.nets_distribution[self.net_id][T] += 1
    #
    #     if result.nets_distribution[self.net_id][F] == 0:
    #         for nei in self.cells:
    #             if nei.is_unlocked():
    #                 nei.adjust_gain(result.blocks, -1)
    #     elif result.nets_distribution[self.net_id][F] == 1:
    #         for nei in self.cells:
    #             if nei.is_unlocked() and nei.block_id == F:
    #                 nei.adjust_gain(result.blocks, 1)
