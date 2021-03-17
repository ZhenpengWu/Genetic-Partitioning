import logging

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
        for block in self.__blocks:
            block.reset()

        for block, cids in enumerate(self.__best_partition):
            for cid in cids:
                self.__nodes_block_id[cid] = block

    def store_best_cut(self):
        self.mincut = self.cutsize
        block0 = list(self.__blocks[0].copy_set())
        block1 = list(self.__blocks[1].copy_set())
        self.__best_partition = [block0, block1]

    def update_cutsize_by_gain(self, cell):
        self.cutsize -= self.__nodes_gain[cell.cell_id]

    def has_unlocked_nodes(self):
        return (
            self.__blocks[0].has_unlocked_nodes()
            or self.__blocks[1].has_unlocked_nodes()
        )

    def is_node_locked(self, cell):
        return self.__nodes_locked[cell.cell_id]

    def is_node_unlocked(self, cell):
        return not self.__nodes_locked[cell.cell_id]

    def unlock_node(self, cell):
        self.__nodes_locked[cell.cell_id] = False

    def lock_node(self, cell):
        self.__nodes_locked[cell.cell_id] = True

    def add_locked_node(self, block_id, cell):
        self.__blocks[block_id].add_locked_node(cell, self)

    def add_unlocked_node(self, block_id, cell):
        self.__blocks[block_id].add_unlocked_node(cell, self)

    def get_net_distribution(self, net, block_id):
        return self.__nets_distribution[net.net_id][block_id]

    def inc_net_distribution(self, net, block_id):
        self.__nets_distribution[net.net_id][block_id] += 1

    def dec_net_distribution(self, net, block_id):
        self.__nets_distribution[net.net_id][block_id] -= 1

    def reset_net_distribution(self, net):
        self.__nets_distribution[net.net_id] = [0, 0]

    def update_node_gain(self, cell, adjust):
        block_id = self.get_node_block_id(cell)
        self.__blocks[block_id].remove_node(cell, self)
        self.__nodes_gain[cell.cell_id] += adjust
        self.__blocks[block_id].add_unlocked_node(cell, self)

    def get_node_gain(self, cell):
        return self.__nodes_gain[cell.cell_id]

    def inc_node_gain(self, cell):
        self.__nodes_gain[cell.cell_id] += 1

    def dec_node_gain(self, cell):
        self.__nodes_gain[cell.cell_id] -= 1

    def reset_node_gain(self, cell):
        self.__nodes_gain[cell.cell_id] = 0

    def set_node_block_id(self, cell, block_id):
        self.__nodes_block_id[cell.cell_id] = block_id

    def get_node_block_id(self, cell):
        return self.__nodes_block_id[cell.cell_id]

    def get_node_block_ids(self):
        return self.__nodes_block_id

    def get_block_size(self, block_id):
        return self.__blocks[block_id].size()

    def peek_block_max_gain(self, block_id):
        return self.__blocks[block_id].get_max_gain()

    def pop_block_max_gain(self, block_id):
        return self.__blocks[block_id].pop_max_gain_node()

    def print_blocks_size(self):
        logging.debug(
            "block 0: {}, block 1: {}".format(
                self.__blocks[0].size(), self.__blocks[1].size()
            )
        )
