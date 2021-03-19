class Net:
    def __init__(self, net_id, color):
        self.net_id = net_id
        self.cells = []
        self.color = color

    def add_cell(self, cell):
        """
        add the cell into the cell list of this net
        """
        self.cells.append(cell)

    def get_source(self):
        """
        :return: the source, which is the first cell in the cells
        """
        return self.cells[0]

    def get_sinks(self):
        """
        :return: the sinks, which are the cell except the first one
        """
        return self.cells[1:]
