import logging

from model.circuit import Circuit
from util.data import Data


def partition(circuit: Circuit, app=None):
    data: Data = Data(circuit)

    data.init_partition(circuit)
    data.init_gains(circuit)

    data.calculate_cutsize(circuit)
    logging.info("initial cutsize = {}".format(data.cutsize))

    data.save_best_cut()  # intialize best partition, mincut and prev mincut
    data.prev_mincut = data.mincut = data.cutsize

    if app is not None:
        app.update_canvas(data)
        app.root.after(100, KL_inner, circuit, data, app)
    else:
        KL_inner(circuit, data)


def KL_inner(circuit: Circuit, data: Data, app=None):
    max_gain_node = data.get_max_gain_node()
    data.move_node_another_block(max_gain_node)  # move node to other block, lock it and update gains
    data.update_cutsize_by_gain(max_gain_node)

    if data.cutsize < data.mincut:  # if cutsize is the minimum for this pass, save partition
        data.save_best_cut()

    data.print_blocks_size()

    if app is not None:
        app.update_canvas(data)
        if data.has_unlocked_nodes():
            app.root.after(1, KL_inner, circuit, data, app)
        else:
            app.root.after(1000, KL_reset, circuit, data, app)
    else:
        if data.has_unlocked_nodes():
            KL_inner(circuit, data)
        else:
            KL_reset(circuit, data)


def KL_reset(circuit: Circuit, data: Data, app=None):
    data.restore_blocks()  # restore block data structures
    data.init_gains(circuit)  # calculate initial gains
    data.cutsize = data.mincut  # update cutsize
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
