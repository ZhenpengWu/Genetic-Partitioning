from model.bucket import Bucket


class Block:

    def __init__(self, pmax):
        self.__node_ids = set()
        self.__bucket = Bucket(pmax)

    def reset(self):
        self.__node_ids = set()
        self.__bucket.reset()

    def size(self):
        """Return number of nodes in block."""
        return len(self.__node_ids)

    def add_unlocked_node(self, cell, data):
        """Add specified unlocked node to the block."""
        if data.is_node_locked(cell):
            raise ValueError
        self.__node_ids.add(cell.cell_id)
        self.__bucket.add_node(cell, data)

    def add_locked_node(self, cell, data):
        """Add locked noode to the block."""
        if data.is_node_unlocked(cell):
            raise ValueError
        self.__node_ids.add(cell.cell_id)

    def remove_node(self, cell, data):
        """Remove specified node from the block."""
        self.__node_ids.remove(cell.cell_id)
        self.__bucket.remove_node(cell, data)

    def has_unlocked_nodes(self):
        """Return True if there are unlocked nodes, False otherwise."""
        return not self.__bucket.is_empty()

    def pop_max_gain_node(self):
        """Return node with max gain and lock it."""
        cell = self.__bucket.pop()
        self.__node_ids.remove(cell.cell_id)
        return cell

    def get_max_gain(self):
        return self.__bucket.get_max_gain()

    def __contains__(self, cell):
        """Return True if node is in the block, False otherwise."""
        return cell.cell_id in self.__node_ids

    def copy_set(self):
        return self.__node_ids.copy()
