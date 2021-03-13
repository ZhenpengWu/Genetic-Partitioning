import random
from functools import reduce

from model.block import Block


class Data:

    def __init__(self, circuit):
        self.iteration = 1
        pmax = self.__get_pmax(circuit)
        self.blocks = [Block(pmax), Block(pmax)]
        self.cutsize = None
        self.best_partition = None
        self.prev_mincut = None
        self.mincut = None

        self.nets_distribution = [[0, 0]] * circuit.get_nets_size()
        self.node_lock = [False] * circuit.get_cells_size()
        self.node_block = [-1] * circuit.get_cells_size()
        self.node_gain = [0] * circuit.get_cells_size()

    def move_node_another_block(self, cell):
        F = self.get_node_block_id(cell)  # from block id
        T = (F + 1) % 2  # to block id
        self.update_lock_node_block(cell, T)
        for net in cell.nets:
            if self.get_net_distribution(net, T) == 0:
                for nei in net.cells:
                    if self.is_node_unlocked(nei):
                        self.update_node_gain(nei, 1)
            elif self.get_net_distribution(net, T) == 1:
                for nei in net.cells:
                    if self.is_node_unlocked(nei) and self.get_node_block_id(nei) == T:
                        self.update_node_gain(nei, -1)

            self.nets_distribution[net.net_id][F] -= 1
            self.nets_distribution[net.net_id][T] += 1

            if self.get_net_distribution(net, F) == 0:
                for nei in net.cells:
                    if self.is_node_unlocked(nei):
                        self.update_node_gain(nei, -1)
            elif self.get_net_distribution(net, F) == 1:
                for nei in net.cells:
                    if self.is_node_unlocked(nei) and self.get_node_block_id(nei) == F:
                        self.update_node_gain(nei, 1)

    def update_lock_node_block(self, cell, block_id):
        self.node_lock[cell.nid] = True  # lock
        self.node_block[cell.nid] = block_id
        self.blocks[block_id].add_locked_node(cell, self)

    def init_partition(self, circuit):
        n = circuit.get_cells_size()
        random_cids = random.sample(range(n), n)

        for i, cid in enumerate(random_cids):
            self.node_block[cid] = i % 2

    def print_blocks_size(self):
        print(self.blocks[0].size(), self.blocks[1].size())

    def restore_blocks(self):
        for block in self.blocks:
            block.reset()

        # set block ID for each node
        for block, cids in enumerate(self.best_partition):
            for cid in cids:
                self.node_block[cid] = block

    def save_best_cut(self):
        self.mincut = self.cutsize
        block0 = list(self.blocks[0].copy_set())
        block1 = list(self.blocks[1].copy_set())
        self.best_partition = [block0, block1]

    def get_net_distribution(self, net, block_id):
        return self.nets_distribution[net.net_id][block_id]

    def get_max_gain_node(self):
        """Choose node to move based on gain and balance condition and return it."""
        if self.blocks[0].size() > self.blocks[1].size():
            return self.blocks[0].pop_max_gain_node()
        elif self.blocks[0].size() < self.blocks[1].size():
            return self.blocks[1].pop_max_gain_node()
        elif self.blocks[0].get_max_gain() > self.blocks[1].get_max_gain():
            return self.blocks[0].pop_max_gain_node()
        elif self.blocks[0].get_max_gain() < self.blocks[1].get_max_gain():
            return self.blocks[1].pop_max_gain_node()
        else:  # break tie
            return self.blocks[random.choice([0, 1])].pop_max_gain_node()

    def has_unlocked_nodes(self):
        return self.blocks[0].has_unlocked_nodes() or self.blocks[1].has_unlocked_nodes()

    def is_node_locked(self, cell):
        return self.node_lock[cell.nid]

    def is_node_unlocked(self, cell):
        return not self.node_lock[cell.nid]

    def calculate_cutsize(self, circuit):
        self.cutsize = reduce(lambda a, b: a + (1 if self.is_cut(b) else 0), circuit.nets, 0)

    def is_cut(self, net):
        return (self.get_net_distribution(net, 0) > 0) and (self.get_net_distribution(net, 1) > 0)

    def update_cutsize_by_gain(self, cell):
        self.cutsize -= self.node_gain[cell.nid]

    def update_node_gain(self, cell, adjust):
        block_id = self.get_node_block_id(cell)
        self.blocks[block_id].remove_node(cell, self)
        self.node_gain[cell.nid] += adjust
        self.blocks[block_id].add_unlocked_node(cell, self)

    def init_distribution(self, circuit):
        for net in circuit.nets:
            self.nets_distribution[net.net_id] = [0, 0]
            for cell in net.cells:
                block_id = self.get_node_block_id(cell)
                self.nets_distribution[net.net_id][block_id] += 1

    def init_gains(self, circuit):
        self.init_distribution(circuit)

        for cell in circuit.cells:
            self.node_lock[cell.nid] = False  # unlock
            self.node_gain[cell.nid] = 0
            F = self.get_node_block_id(cell)  # from block id
            T = (F + 1) % 2  # to block id
            for net in cell.nets:
                if self.get_net_distribution(net, F) == 1:
                    self.node_gain[cell.nid] += 1
                if self.get_net_distribution(net, T) == 0:
                    self.node_gain[cell.nid] -= 1
            self.blocks[F].add_unlocked_node(cell, self)

    def get_node_gain(self, cell):
        return self.node_gain[cell.nid]

    def get_node_block_id(self, cell):
        return self.node_block[cell.nid]

    @staticmethod
    def __get_pmax(circuit):
        """Return max(number of pins on node(i) for i in layout.netlist"""
        return reduce(lambda a, b: max(a, b.get_net_size()), circuit.cells, 0)
