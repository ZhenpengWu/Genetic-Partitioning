import os
from typing import List

from model.block import Block
from model.cell import Cell
from model.net import Net
from util.colors import random_colors


class Circuit:
    def __init__(self) -> None:
        self.cells: List[Cell] = []
        self.nets: List[Net] = []
        self.benchmark = None
        self.block: List[Block] = []

        self.iteration = None
        self.cutsize = None

    def parse_file(self, file) -> None:
        """
        parse the input file
        :param file: the input file
        """
        self.benchmark = os.path.basename(file)

        with open(file, "r") as f:
            first = f.readline().strip().split()
            self.__init_cells(int(first[0]))
            self.__init_circuit(int(first[1]), f)

    def __init_cells(self, cells) -> None:
        """
        initialized the cell list
        :param cells: the number of cells to be palaced
        """
        self.cells = [Cell(i) for i in range(cells)]

    def __init_circuit(self, connections, f) -> None:
        """
        initialize the netslist
        :param connections: the number of connections / nets
        :param f: the input file
        """
        self.nets = []
        colors = random_colors(connections)

        for i in range(connections):
            self.__read_net(colors[i % len(colors)], f.readline())

    def __read_net(self, color, s) -> None:
        """
        create a net, based on the data, assign an unique color
        then add to netlist
        :param color: unique color for the net
        :param s: string contains data of a net
        """
        data = s.strip().split()

        net: Net = Net(len(self.nets), color)
        for i in data[1:]:
            cell: Cell = self.cells[int(i)]
            cell.add_net(net)
            net.add_cell(cell)

        self.nets.append(net)

    def get_nets_size(self) -> int:
        return len(self.nets)

    def get_cells_size(self) -> int:
        return len(self.cells)
