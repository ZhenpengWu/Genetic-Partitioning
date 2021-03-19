import logging
from typing import List

from model.block import Block


class Data:
    def __init__(self, pmax, nets_size, nodes_block_id):
        self.iteration = 1

        self.__blocks = [Block(pmax), Block(pmax)]
        self.__nets_distribution = [[0, 0]] * nets_size
        self.__nodes_locked = [False] * len(nodes_block_id)
        self.__nodes_gain = [0] * len(nodes_block_id)
        self.__nodes_block_id = nodes_block_id

        self.__best_partition = None
        self.cutsize = None
        self.prev_mincut = None
        self.mincut = None

    def restore_best_cut(self):
        """
        restore the best cut in the current pass
        """
        # reset block data structure
        for block in self.__blocks:
            block.reset()

        # restore block id for each node
        for block, cids in enumerate(self.__best_partition):
            for cid in cids:
                self.__nodes_block_id[cid] = block

        # restore cutsize
        self.cutsize = self.mincut

    def store_best_cut(self):
        """
        store the best cut
        """
        # store block id for each node
        block0 = list(self.__blocks[0].copy_set())
        block1 = list(self.__blocks[1].copy_set())
        self.__best_partition = [block0, block1]

        # store the mincut
        self.mincut = self.cutsize

    def update_cutsize_by_gain(self, cell):
        """
        update the cutsize by the gain, after moving max gain node to another block
        """
        self.cutsize -= self.__nodes_gain[cell.cell_id]

    def has_unlocked_nodes(self) -> bool:
        """
        :return: True if there are unlocked nodes remains in the blocks
        """
        return (
                self.__blocks[0].has_unlocked_nodes()
                or self.__blocks[1].has_unlocked_nodes()
        )

    def is_node_locked(self, cell) -> bool:
        """
        :return: True if cell is locked
        """
        return self.__nodes_locked[cell.cell_id]

    def is_node_unlocked(self, cell) -> bool:
        """
        :return: True if cell is unlocked
        """
        return not self.__nodes_locked[cell.cell_id]

    def unlock_node(self, cell, block_id):
        """
        unlock the cell
        """
        self.__nodes_locked[cell.cell_id] = False
        self.__blocks[block_id].add_unlocked_node(cell, self)

    def lock_node(self, cell, block_id):
        """
        lock the cell
        """
        self.__nodes_locked[cell.cell_id] = True
        self.__nodes_block_id[cell.cell_id] = block_id
        self.__blocks[block_id].add_locked_node(cell, self)

    def get_net_distribution(self, net, block_id) -> int:
        """
        :return: the number of cells in the specified block of the net
        """
        return self.__nets_distribution[net.net_id][block_id]

    def inc_net_distribution(self, net, block_id):
        """
        inc the number of cells in the specified block of the net
        """
        self.__nets_distribution[net.net_id][block_id] += 1

    def dec_net_distribution(self, net, block_id):
        """
        dec the number of cells in the specified block of the net
        """
        self.__nets_distribution[net.net_id][block_id] -= 1

    def reset_net_distribution(self, net):
        """
        reset the net distribution of the given net
        """
        self.__nets_distribution[net.net_id] = [0, 0]

    def update_node_gain(self, cell, adjust):
        """
        update the cell's gain by the adjust value
        """
        block_id = self.get_node_block_id(cell)
        # remove node from the block
        self.__blocks[block_id].remove_node(cell, self)
        # update gain
        self.__nodes_gain[cell.cell_id] += adjust
        # add node to the new position in the bucket
        self.__blocks[block_id].add_unlocked_node(cell, self)

    def get_node_gain(self, cell) -> int:
        """
        :return: gain of the given cell
        """
        return self.__nodes_gain[cell.cell_id]

    def inc_node_gain(self, cell):
        """
        inc gain of the given cell
        """
        self.__nodes_gain[cell.cell_id] += 1

    def dec_node_gain(self, cell):
        """
        dec gain of the given cell
        """
        self.__nodes_gain[cell.cell_id] -= 1

    def reset_node_gain(self, cell):
        """
        reset gain of the given cell
        """
        self.__nodes_gain[cell.cell_id] = 0

    def get_node_block_id(self, cell) -> int:
        """
        :return: the block id of the given cell
        """
        return self.__nodes_block_id[cell.cell_id]

    def get_node_block_ids(self) -> List[int]:
        """
        :return: the cells' block id
        """
        return self.__nodes_block_id

    def get_block_size(self, block_id) -> int:
        """
        :return: the size of the given block
        """
        return self.__blocks[block_id].size()

    def peek_block_max_gain(self, block_id) -> int:
        """
        :return: the max gain the given block
        """
        return self.__blocks[block_id].get_max_gain()

    def pop_block_max_gain(self, block_id):
        """
        :return: the max gain node the given block
        """
        return self.__blocks[block_id].pop_max_gain_node()

    def print_blocks_size(self):
        """
        print the size of each block
        """
        logging.debug(
            "block 0: {}, block 1: {}".format(
                self.get_block_size(0), self.get_block_size(1)
            )
        )
