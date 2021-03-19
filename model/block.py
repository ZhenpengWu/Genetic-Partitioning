class Block:
    def __init__(self, pmax):
        self.__node_ids = set()
        self.__buckets: dict = {i: dict() for i in range(-pmax, pmax + 1)}
        self.__max_gain = -pmax
        self.__pmax = pmax
        self.__count = 0

    def reset(self):
        """
        reset the block
        """
        self.__init__(self.__pmax)

    def size(self) -> int:
        """
        :return: the number of nodes in the block
        """
        return len(self.__node_ids)

    def add_unlocked_node(self, cell, data):
        """
        add specified unlocked node to the block
        """
        if data.is_node_locked(cell):
            raise ValueError
        self.__node_ids.add(cell.cell_id)
        gain = data.get_node_gain(cell)
        self.__buckets[gain][cell.cell_id] = cell
        self.__count += 1
        self.__max_gain = max(gain, self.__max_gain)  # update max gain pointer

    def add_locked_node(self, cell, data):
        """
        add specified locked noode to the block
        """
        if data.is_node_unlocked(cell):
            raise ValueError
        self.__node_ids.add(cell.cell_id)

    def remove_node(self, cell, data):
        """
        remove specified node from the block
        """
        gain = data.get_node_gain(cell)
        del self.__buckets[gain][cell.cell_id]
        self.__remove_node(cell)

    def has_unlocked_nodes(self) -> bool:
        """
        :return: True if there are unlocked nodes, otherwise False
        """
        return self.__count != 0

    def pop_max_gain_node(self):
        """
        :return: node with the max gain in the block
        """
        (_, node) = self.__buckets[self.__max_gain].popitem()
        self.__remove_node(node)
        return node

    def __remove_node(self, cell):
        self.__node_ids.remove(cell.cell_id)
        self.__update_max_gain()
        self.__count -= 1

    def __update_max_gain(self):
        """
        update max gain until finding not empty bucket
        """
        while (self.__max_gain > -self.__pmax) and (
                not self.__buckets[self.__max_gain]
        ):
            self.__max_gain -= 1

    def get_max_gain(self) -> int:
        """
        :return: the maximum gain in the block
        """
        return self.__max_gain

    def copy_set(self):
        """
        :return: copy of node list in the block
        """
        return self.__node_ids.copy()
