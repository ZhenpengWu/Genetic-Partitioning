from model.block import Block


class Data:

    def __init__(self, pmax, nets_size, nodes_block_id):
        self.iteration = 1

        self.blocks = [Block(pmax), Block(pmax)]
        self.nets_distribution = [[0, 0]] * nets_size
        cells_size = len(nodes_block_id)
        self.nodes_locked = [False] * cells_size
        self.nodes_gain = [0] * cells_size
        self.nodes_block_id = nodes_block_id

        self.best_partition = None
        self.cutsize = None
        self.prev_mincut = None
        self.mincut = None

    def restore_best_cut(self):
        for block in self.blocks:
            block.reset()

        for block, cids in enumerate(self.best_partition):
            for cid in cids:
                self.nodes_block_id[cid] = block

    def store_best_cut(self):
        self.mincut = self.cutsize
        block0 = list(self.blocks[0].copy_set())
        block1 = list(self.blocks[1].copy_set())
        self.best_partition = [block0, block1]

    def update_cutsize_by_gain(self, cell):
        self.cutsize -= self.nodes_gain[cell.cell_id]

    def set_cutsize(self, cutsize):
        self.cutsize = cutsize

    def has_unlocked_nodes(self):
        return self.blocks[0].has_unlocked_nodes() or self.blocks[1].has_unlocked_nodes()

    def is_node_locked(self, cell):
        return self.nodes_locked[cell.cell_id]

    def is_node_unlocked(self, cell):
        return not self.nodes_locked[cell.cell_id]

    def unlock_node(self, cell):
        self.nodes_locked[cell.cell_id] = False

    def lock_node(self, cell):
        self.nodes_locked[cell.cell_id] = True

    def add_locked_node(self, block_id, cell):
        self.blocks[block_id].add_locked_node(cell, self)

    def add_unlocked_node(self, block_id, cell):
        self.blocks[block_id].add_unlocked_node(cell, self)

    def get_net_distribution(self, net, block_id):
        return self.nets_distribution[net.net_id][block_id]

    def inc_net_distribution(self, net, block_id):
        self.nets_distribution[net.net_id][block_id] += 1

    def dec_net_distribution(self, net, block_id):
        self.nets_distribution[net.net_id][block_id] -= 1

    def reset_net_distribution(self, net):
        self.nets_distribution[net.net_id] = [0, 0]

    def update_node_gain(self, cell, adjust):
        block_id = self.get_node_block_id(cell)
        self.blocks[block_id].remove_node(cell, self)
        self.nodes_gain[cell.cell_id] += adjust
        self.blocks[block_id].add_unlocked_node(cell, self)

    def get_node_gain(self, cell):
        return self.nodes_gain[cell.cell_id]

    def inc_node_gain(self, cell):
        self.nodes_gain[cell.cell_id] += 1

    def dec_node_gain(self, cell):
        self.nodes_gain[cell.cell_id] -= 1

    def reset_node_gain(self, cell):
        self.nodes_gain[cell.cell_id] = 0

    def set_node_block_id(self, cell, block_id):
        self.nodes_block_id[cell.cell_id] = block_id

    def get_node_block_id(self, cell):
        return self.nodes_block_id[cell.cell_id]

    def get_block_size(self, block_id):
        return self.blocks[block_id].size()

    def peek_block_max_gain(self, block_id):
        return self.blocks[block_id].get_max_gain()

    def pop_block_max_gain(self, block_id):
        return self.blocks[block_id].pop_max_gain_node()

    def print_blocks_size(self):
        print(self.blocks[0].size(), self.blocks[1].size())
