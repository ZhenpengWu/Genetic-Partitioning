class Bucket:
    """
    Class representing a Bucket List.

    Used to organize nodes by their gain value. Consists of an array of
    dictionaries. This array is implemented as a dictionary itself so that
    negative gain values may be used to indexes (keys).
    """

    def __init__(self, pmax):
        self.__bucket_list = {i: dict() for i in range(-pmax, pmax + 1)}
        self.__max_gain = -pmax
        self.__pmax = pmax
        self.__count = 0

    def reset(self):
        self.__init__(self.__pmax)

    def is_empty(self):
        """Return True if the bucket list is empty, False otherwise."""
        return self.__count == 0

    def add_node(self, cell, data):
        """Add a node with initial gain to the Bucket List."""
        # add node
        gain = data.get_node_gain(cell)
        self.__bucket_list[gain][cell.cell_id] = cell

        self.__count += 1
        # update max gain pointer
        if gain > self.__max_gain:
            self.__max_gain = gain

    def __update_max_gain(self):
        """Update max gain if removing last node from the max gain bucket."""
        while (self.__max_gain > -self.__pmax) and (not self.__bucket_list[self.__max_gain]):
            self.__max_gain -= 1

    def remove_node(self, cell, data):
        """Remove a node from the Bucket List."""
        # remove node
        gain = data.get_node_gain(cell)
        del self.__bucket_list[gain][cell.cell_id]
        self.__update_max_gain()
        self.__count -= 1

    def pop(self):
        """Return a node with highest gain and remove it."""
        (ID, node) = self.__bucket_list[self.__max_gain].popitem()

        self.__update_max_gain()
        self.__count -= 1
        return node

    def get_max_gain(self):
        return self.__max_gain
