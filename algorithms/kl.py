import logging
import random
from functools import reduce

from model.cell import Cell
from model.circuit import Circuit
from model.data import Data
from model.net import Net


def kl(circuit: Circuit, app=None):
    """
    perform the Kernighan-Lin Partition algorithm in the given circuit
    """
    data = init_partition(circuit)

    if app is not None:
        app.update_canvas(data)
        app.root.after(100, kl_inner_loop, circuit, data, app)
    else:
        kl_inner_loop(circuit, data)


def kl_inner_loop(circuit: Circuit, data: Data, app=None, genetic=False):
    """
    perform the inner loop of the Kernighan-Lin Partition algorithm
    """
    # select the max gain node from blocks
    max_gain_node = select_max_gain_node(data)

    # move the max gain node to another block
    #   - update the gain for each node
    #   - update the nets distribution
    #   - update the cutsize
    move_node_another_block(max_gain_node, data)

    # if cutsize is the minimum for this pass, store the cut
    if data.cutsize < data.mincut:
        data.store_best_cut()

    data.print_blocks_size()

    if app is not None:
        app.update_canvas(data)
        # inner loop stop until no unlocked nodes remains
        if data.has_unlocked_nodes():
            app.root.after(1, kl_inner_loop, circuit, data, app, genetic)
        else:  # ineer loop exit
            app.root.after(1000, kl_inner_stop, circuit, data, app, genetic)
    elif data.has_unlocked_nodes():
        kl_inner_loop(circuit, data, app, genetic)
    else:
        kl_inner_stop(circuit, data, app, genetic)


def kl_inner_stop(circuit: Circuit, data: Data, app=None, genetic=False):
    """
    it is the end of the current pass, restore the best cut of this pass;
    terminates the outer loop if mincut doesn't improve or it reaches 6 iterations
    """
    data.restore_best_cut()  # restore block data structures

    # update the distribution for the restored best cut
    update_distribution(circuit, data)
    # update the gains for the restored best cut
    calculate_gains(circuit, data)

    if genetic:
        return

    logging.info("iteration {}: best mincut = {}".format(data.iteration, data.cutsize))

    if app is not None:
        app.update_canvas(data)
    data.iteration += 1

    # continue for up to 6 iterations or until mincut stops improving
    if data.iteration <= 6 and data.mincut != data.prev_mincut:
        data.prev_mincut = data.mincut
        if app is not None:
            app.root.after(1000, kl_inner_loop, circuit, data, app)
    elif app is not None:
        app.update_partition_button(True)


def init_partition(circuit, block_ids=None) -> Data:
    """
    randomly partition the nodes equally, if the block_ids
    is not specified.
    :return: data container for the current partition
    """
    pmax = get_pmax(circuit)
    nets_size = circuit.get_nets_size()
    n = circuit.get_cells_size()

    if block_ids is None:
        random_cids = random.sample(range(n), n)
        block_ids = [cid % 2 for i, cid in enumerate(random_cids)]

    # initialzie a data container for the current partition
    data = Data(pmax, nets_size, block_ids)
    # update the nets distribution in the current partition
    update_distribution(circuit, data)
    # update the gain for each node in the current partition
    calculate_gains(circuit, data)
    # update the cutsize of the current partition
    data.cutsize = calculate_cutsize(circuit, data)

    logging.info("initial cutsize = {}".format(data.cutsize))

    # intialize best partition, and prev mincut
    data.store_best_cut()
    data.prev_mincut = data.mincut

    return data


def select_max_gain_node(data: Data):
    """
    choose max gain node from blocks, and maintain the balance constraint
    """
    block0_size, block0_max_gain = data.get_block_size(0), data.peek_block_max_gain(0)
    block1_size, block1_max_gain = data.get_block_size(1), data.peek_block_max_gain(1)

    if block0_size > block1_size or (
            block0_size == block1_size and block0_max_gain > block1_max_gain):
        return data.pop_block_max_gain(0)
    elif block0_size < block1_size or (
            block0_size == block1_size and block0_max_gain < block1_max_gain):
        return data.pop_block_max_gain(1)
    else:  # break tie
        return data.pop_block_max_gain(random.choice([0, 1]))


def move_node_another_block(cell: Cell, data: Data):
    """
    move the max gain node to anothe block
    """
    F = data.get_node_block_id(cell)  # from block id
    T = (F + 1) % 2  # to block id

    # lock the node
    data.lock_node(cell, T)

    for net in cell.nets:
        # check critical nets before the move
        if data.get_net_distribution(net, T) == 0:
            for nei in net.cells:
                if data.is_node_unlocked(nei):
                    data.update_node_gain(nei, 1)
        elif data.get_net_distribution(net, T) == 1:
            for nei in net.cells:
                if data.is_node_unlocked(nei) and data.get_node_block_id(nei) == T:
                    data.update_node_gain(nei, -1)

        # change the net distribution to reflect the move
        data.dec_net_distribution(net, F)
        data.inc_net_distribution(net, T)

        # check the critical nets after the move
        if data.get_net_distribution(net, F) == 0:
            for nei in net.cells:
                if data.is_node_unlocked(nei):
                    data.update_node_gain(nei, -1)
        elif data.get_net_distribution(net, F) == 1:
            for nei in net.cells:
                if data.is_node_unlocked(nei) and data.get_node_block_id(nei) == F:
                    data.update_node_gain(nei, 1)

    data.update_cutsize_by_gain(cell)


def update_distribution(circuit: Circuit, data: Data):
    """
    update the distribution for each net
    """
    for net in circuit.nets:
        data.reset_net_distribution(net)
        for cell in net.cells:
            block_id = data.get_node_block_id(cell)
            data.inc_net_distribution(net, block_id)


def calculate_gains(circuit: Circuit, data: Data):
    """
    calculate the gain for each node
    """
    for cell in circuit.cells:
        data.reset_node_gain(cell)
        F = data.get_node_block_id(cell)  # from block id
        T = (F + 1) % 2  # to block id
        for net in cell.nets:
            if data.get_net_distribution(net, F) == 1:
                data.inc_node_gain(cell)
            if data.get_net_distribution(net, T) == 0:
                data.dec_node_gain(cell)
        data.unlock_node(cell, F)


def calculate_cutsize(circuit: Circuit, data: Data):
    """
    :return: the cutsize fo the current partition
    """
    return reduce(lambda a, b: a + is_cut(b, data), circuit.nets, 0)


def is_cut(net: Net, data: Data) -> bool:
    """
    :return: True if the given net is a cut, otherwiese False
    """
    return (data.get_net_distribution(net, 0) > 0) and (
            data.get_net_distribution(net, 1) > 0
    )


def get_pmax(circuit: Circuit) -> int:
    """
    :return: pmax, which is the maximum net size
    """
    return reduce(lambda a, b: max(a, b.get_nets_size()), circuit.cells, 0)
