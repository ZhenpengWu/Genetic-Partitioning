import bisect
import logging
import random
from collections import Counter
from functools import reduce
from typing import List

from algorithms.kl import init_partition, kl_inner_loop
from model.circuit import Circuit
from model.data import Data


def genetic(circuit: Circuit, app=None):
    """
    perform the Genetic Partition algorithm in the given circuit
    """
    # come up a random population
    population = random_population(circuit)

    if app is not None:
        app.root.after(100, genetic_loop, circuit, population, app)
    else:
        genetic_loop(circuit, population, app)


def genetic_loop(circuit, population, app=None):
    """
    perform the loop of the Genetric Partition algorithm
    """
    # select two members from the population
    parents, fitness_list = select_parents(population)
    # combine parents to produce 2 offspring
    offspring = crossover(population, parents)
    # perform mutation operation on offspring
    mutation(offspring)
    # perfrom local improvement on offspring
    offspring = local_improvement(circuit, offspring)
    # replace some members in population with offspring
    replace(population, fitness_list, parents, offspring)
    # check the stopping criterion
    stop, best = stopping_criterion(population)

    if app is not None:
        # render the best chromeosome among the population
        app.update_canvas(best)
        if not stop:
            app.root.after(100, genetic_loop, circuit, population, app)
        else:
            app.update_partition_button(True)
    elif not stop:
        genetic_loop(circuit, population)


def stopping_criterion(population):
    """
    the genetic algorithm stopped when 80% of the population is
    occupied by solution with the same quality
    """
    best, freq = None, Counter()
    for chromosome in population:
        if not best or chromosome.mincut < best.mincut:
            best = chromosome
        freq[chromosome.mincut] += 1
    rate = (freq[best.mincut] + freq[best.mincut + 1]) / 50
    logging.info("mincut: {} | rate: {:.2%}".format(best.mincut, rate))
    return rate >= 0.8, best


def random_population(circuit: Circuit, k=50) -> List[Data]:
    """
    initialize population as k chromosomes, each representing a potential solution
    """
    population = [init_partition(circuit) for _ in range(k)]
    return population


def select_parents(population):
    """
    select parents from the population, based on the fitness function
    """
    # calculate the worst and best cutsize
    worst_cutsize, best_cutsize = population[0].mincut, population[0].mincut
    for chromosome in population:
        worst_cutsize = max(chromosome.mincut, worst_cutsize)
        best_cutsize = min(chromosome.mincut, best_cutsize)

    # calculate fitness value for each chromeosome in population
    F, fitness_list, search_list = 0, [], []
    for chromosome in population:
        f = fitness(chromosome, worst_cutsize, best_cutsize)
        F += f
        fitness_list.append(f)
        search_list.append(F)

    # select two parents
    parents = [search_parent(search_list, F), search_parent(search_list, F)]

    return parents, fitness_list


def fitness(chromosome: Data, worst_cutsize, best_cutsize) -> int:
    """
    :return: fitness_i = (C_w - C_i) + (C_w - C_b) // 3
    """
    return (worst_cutsize - chromosome.mincut) + (worst_cutsize - best_cutsize) // 3


def search_parent(search_list, F):
    """
    select a parent with the probability that is propotional to its fitness value
    :return: the index of parent selected
    """
    return bisect.bisect_left(search_list, random.random() * F)


def crossover(population, parent_indexes, k=5):
    """
    perfrom 5-point crossover to produce 2 offspring
    :return: generated offsping
    """
    parents = [population[p].get_node_block_ids() for p in parent_indexes]
    n = len(parents[0])  # cell size
    crossover_points = sorted(random.sample(range(n), k))

    offspring = [], []
    j = 0
    for i in range(n):
        offspring[0].append(parents[j % 2][i])
        offspring[1].append(
            parents[j % 2][i] if j % 2 == 0 else flip(parents[j % 2][i])
        )
        if j < k and i == crossover_points[j]:
            j += 1

    return offspring


def mutation(offspring):
    """
    perfrom mutation operation on offspring, and maintain the balance constraint
    """
    for child in offspring:
        n = len(child)
        # perform mutation operation
        m = random.randint(0, n // 100)
        for i in random.sample(range(n), m):
            child[i] = flip(child[i])

        # balance the child
        diff = reduce(lambda a, b: a + (1 if b == 1 else -1), child, 0)
        block_id, diff = 1 if diff > 0 else 0, abs(diff)

        for i in random.sample(range(n), n):
            if (n % 2 == 0 and diff == 0) or (n % 2 == 1 and diff <= 1):
                break
            if child[i] == block_id:
                child[i] = flip(child[i])
                diff -= 2


def flip(block_id) -> int:
    return (block_id + 1) % 2


def local_improvement(circuit, offspring):
    """
    perform one pass of KL partition on the offspring
    :return: data containers for offspring
    """
    res = [init_partition(circuit, child) for child in offspring]
    index = 0 if res[0].mincut < res[1].mincut else 1
    kl_inner_loop(circuit, res[index], None, True)
    return res[index]


def replace(population, fitness_list, parents_index, offspring):
    """
    replace some members with offsping:
        - if the offsping is better than one of the parents,
            -  repace more similar parent with the offspring
        - else, replace with the most inferior member of the population
    """
    parents = population[parents_index[0]], population[parents_index[1]]

    distance0, distance1 = (
        measure_distance(parents[0], offspring),
        measure_distance(parents[1], offspring),
    )
    if offspring.mincut < parents[0 if distance0 < distance1 else 1].mincut:
        index = parents_index[0 if distance0 < distance1 else 1]
    elif offspring.mincut < parents[1 if distance0 < distance1 else 0].mincut:
        index = parents_index[1 if distance0 < distance1 else 0]
    else:
        index = find_inferior(fitness_list)
    population[index] = offspring


def measure_distance(parent, child) -> int:
    """
    :return: the Hamming distance between parent and child
    """
    parent_block_ids, child_block_ids = (
        parent.get_node_block_ids(),
        child.get_node_block_ids(),
    )
    n = len(parent_block_ids)
    return sum([parent_block_ids[i] != child_block_ids[i] for i in range(n)])


def find_inferior(fitness_list) -> int:
    """
    :return: the index of the most inferior member
    """
    min1 = -1
    for i, v in enumerate(fitness_list):
        if min1 < -1 or v < fitness_list[min1]:
            min1 = i
    return min1
