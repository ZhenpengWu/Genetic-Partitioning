import logging
import random
from functools import reduce

from model.circuit import Circuit
from model.data import Data


def partition(circuit: Circuit, app=None):
    data = init_partition(circuit)

    if app is not None:
        app.update_canvas(data)
        app.root.after(100, KL_inner, circuit, data, app)
    else:
        KL_inner(circuit, data)


def KL_inner(circuit: Circuit, data, app=None, genetic=False):
    max_gain_node = get_max_gain_node(data)
    move_node_another_block(max_gain_node, data)
    data.update_cutsize_by_gain(max_gain_node)

    if data.cutsize < data.mincut:  # if cutsize is the minimum for this pass, save partition
        data.store_best_cut()

    # data.print_blocks_size()

    if app is not None:
        # if not genetic:
        app.update_canvas(data)
        if data.has_unlocked_nodes():
            app.root.after(1, KL_inner, circuit, data, app, genetic)
        else:
            app.root.after(1000, KL_reset, circuit, data, app, genetic)
    else:
        if data.has_unlocked_nodes():
            KL_inner(circuit, data, app, genetic)
        else:
            KL_reset(circuit, data, app, genetic)


def KL_reset(circuit: Circuit, data, app=None, genetic=False):
    data.restore_best_cut()  # restore block data structures

    update_distribution(circuit, data)
    calculate_gains(circuit, data)  # calculate initial gains

    data.cutsize = data.mincut

    if genetic:
        return

    logging.info(
        "iteration {}: best min cut seen = {}".format(data.iteration, data.cutsize)
    )
    if app is not None:
        app.update_canvas(data)

    # continue for up to 6 iterations or until mincut stops improving
    if data.iteration < 6 and data.mincut != data.prev_mincut:
        data.iteration += 1
        data.prev_mincut = data.mincut
        if app is not None:
            app.update_iteration(data.iteration)
            app.root.after(1000, KL_inner, circuit, data, app)


def init_partition(circuit, block_ids=None):
    pmax = get_pmax(circuit)
    nets_size = circuit.get_nets_size()
    n = circuit.get_cells_size()

    if block_ids is None:
        random_cids = random.sample(range(n), n)
        block_ids = []
        for i, cid in enumerate(random_cids):
            block_ids.append(cid % 2)

    data = Data(pmax, nets_size, block_ids)
    update_distribution(circuit, data)
    calculate_gains(circuit, data)

    data.cutsize = calculate_cutsize(circuit, data)
    print("initial cutsize = {}".format(data.cutsize))

    data.store_best_cut()  # intialize best partition, mincut and prev mincut
    data.prev_mincut = data.mincut = data.cutsize

    return data


def get_max_gain_node(data):
    """Choose node to move based on gain and balance condition and return it."""
    block0_size = data.get_block_size(0)
    block1_size = data.get_block_size(1)

    if block0_size > block1_size:
        return data.pop_block_max_gain(0)
    elif block0_size < block1_size:
        return data.pop_block_max_gain(1)

    block0_max_gain = data.peek_block_max_gain(0)
    block1_max_gain = data.peek_block_max_gain(1)

    if block0_max_gain > block1_max_gain:
        return data.pop_block_max_gain(0)
    elif block0_max_gain < block1_max_gain:
        return data.pop_block_max_gain(1)
    else:  # break tie
        return data.pop_block_max_gain(random.choice([0, 1]))


def move_node_another_block(cell, data):
    F = data.get_node_block_id(cell)  # from block id
    T = (F + 1) % 2  # to block id

    data.lock_node(cell)
    data.set_node_block_id(cell, T)
    data.add_locked_node(T, cell)

    for net in cell.nets:
        if data.get_net_distribution(net, T) == 0:
            for nei in net.cells:
                if data.is_node_unlocked(nei):
                    data.update_node_gain(nei, 1)
        elif data.get_net_distribution(net, T) == 1:
            for nei in net.cells:
                if data.is_node_unlocked(nei) and data.get_node_block_id(nei) == T:
                    data.update_node_gain(nei, -1)

        data.dec_net_distribution(net, F)
        data.inc_net_distribution(net, T)

        if data.get_net_distribution(net, F) == 0:
            for nei in net.cells:
                if data.is_node_unlocked(nei):
                    data.update_node_gain(nei, -1)
        elif data.get_net_distribution(net, F) == 1:
            for nei in net.cells:
                if data.is_node_unlocked(nei) and data.get_node_block_id(nei) == F:
                    data.update_node_gain(nei, 1)


def update_distribution(circuit, data):
    for net in circuit.nets:
        data.reset_net_distribution(net)
        for cell in net.cells:
            block_id = data.get_node_block_id(cell)
            data.inc_net_distribution(net, block_id)


def calculate_gains(circuit, data):
    for cell in circuit.cells:
        data.unlock_node(cell)
        data.reset_node_gain(cell)
        F = data.get_node_block_id(cell)  # from block id
        T = (F + 1) % 2  # to block id
        for net in cell.nets:
            if data.get_net_distribution(net, F) == 1:
                data.inc_node_gain(cell)
            if data.get_net_distribution(net, T) == 0:
                data.dec_node_gain(cell)
        data.add_unlocked_node(F, cell)


def calculate_cutsize(circuit, data):
    return reduce(lambda a, b: a + (1 if is_cut(b, data) else 0), circuit.nets, 0)


def is_cut(net, data):
    return (data.get_net_distribution(net, 0) > 0) and (data.get_net_distribution(net, 1) > 0)


def get_pmax(circuit):
    return reduce(lambda a, b: max(a, b.get_net_size()), circuit.cells, 0)
