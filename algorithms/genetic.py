import bisect
import logging
import random
from collections import Counter
from functools import reduce

from algorithms.kl import init_partition, kl_inner
from model.circuit import Circuit


def genetic(circuit: Circuit, app=None):
    # Step 1: come up a random population
    population = random_population(circuit)

    if app is not None:
        app.root.after(100, genetic_inner, circuit, population, app)
    else:
        genetic_inner(circuit, population, app)


def genetic_inner(circuit, population, app=None):
    parents, fitness_list = select_parent(population)
    offsprings = crossover(population, parents)
    mutation(offsprings)
    offsprings = local_imporvement(circuit, offsprings)
    replace_with_offsprings(population, fitness_list, parents, offsprings)

    stop, best = stopping_criterion(population)

    if app is not None:
        app.update_canvas(best)
        if not stop:
            app.root.after(100, genetic_inner, circuit, population, app)
        else:
            app.update_partition_button(True)
    elif not stop:
        genetic_inner(circuit, population)


def stopping_criterion(population):
    best, freq = None, Counter()
    for chromeosome in population:
        if not best or chromeosome.mincut < best.mincut:
            best = chromeosome
        freq[chromeosome.mincut] += 1
    rate = (freq[best.mincut] + freq[best.mincut + 1]) / 50
    logging.info("mincut: {} | rate: {:.2%}".format(best.mincut, rate))
    return rate >= 0.8, best


def local_imporvement(circuit, offsprings):
    res = [init_partition(circuit, offspring) for offspring in offsprings]
    for data in res:
        kl_inner(circuit, data, None, True)
    return res


def replace_with_offsprings(population, fitness_list, parents_index, offsprings):
    parents = population[parents_index[0]], population[parents_index[1]]
    used = set()

    for offspring in offsprings:
        distance0, distance1 = (
            measure_distance(parents[0], offspring),
            measure_distance(parents[1], offspring),
        )
        if offspring.mincut < parents[0 if distance0 < distance1 else 1].mincut:
            index = parents_index[0 if distance0 < distance1 else 1]
        elif offspring.mincut < parents[1 if distance0 < distance1 else 0].mincut:
            index = parents_index[1 if distance0 < distance1 else 0]
        else:
            index = find_inferior(fitness_list, used)
        population[index] = offspring
        used.add(index)


def measure_distance(parent, offspring):
    parent_blocks, offspring_blocks = (
        parent.get_node_block_ids(),
        offspring.get_node_block_ids(),
    )
    n = len(parent_blocks)
    return sum([parent_blocks[i] != offspring_blocks[i] for i in range(n)])


def find_inferior(fitness_list, used):
    min1 = -1
    for i, v in enumerate(fitness_list):
        if (i not in used) and (min1 < -1 or v < fitness_list[min1]):
            min1 = i
    return min1


def random_population(circuit: Circuit, k=50):
    popultation = [init_partition(circuit) for _ in range(k)]
    return popultation


def select_parent(population):
    fitness_list, total_fitness, search_list = calculate_fitness(population)

    parents = [
        search_parent(search_list, total_fitness),
        search_parent(search_list, total_fitness),
    ]

    return parents, fitness_list


def calculate_fitness(population):
    worst_cutsize, best_cutsize = population[0].mincut, population[0].mincut
    for chromeosome in population:
        worst_cutsize = max(chromeosome.mincut, worst_cutsize)
        best_cutsize = min(chromeosome.mincut, best_cutsize)

    fitness_list, search_list = [], []
    total_fitness = 0
    for chromeosome in population:
        worst_cutsize = max(chromeosome.mincut, worst_cutsize)
        best_cutsize = min(chromeosome.mincut, best_cutsize)
        fitness = (worst_cutsize - chromeosome.mincut) + (
            worst_cutsize - best_cutsize
        ) // 3
        fitness_list.append(fitness)
        total_fitness += fitness
        search_list.append(total_fitness)

    return fitness_list, total_fitness, search_list


def crossover(population, parent_indexes, k=5):
    # 5-point crossover
    parents = [population[p].get_node_block_ids() for p in parent_indexes]
    n = len(parents[0])  # cell size
    crossover_points = sorted(random.sample(range(n), k))

    offsprings = [], []
    j = 0
    for i in range(n):
        offsprings[0].append(parents[j % 2][i])
        offsprings[1].append(
            parents[j % 2][i] if j % 2 == 0 else flip(parents[j % 2][i])
        )
        if j < k and i == crossover_points[j]:
            j += 1

    return offsprings


def mutation(offsprings):
    for offspring in offsprings:
        n = len(offspring)
        m = random.randint(0, n // 100)
        for _ in range(m):
            i = random.randrange(0, n)
            offspring[i] = flip(offspring[i])

        # balance
        diff = reduce(lambda a, b: a + (1 if b == 1 else -1), offspring, 0)
        block_id, diff = 1 if diff > 0 else 0, abs(diff)

        for i in random.sample(range(n), n):
            if (n % 2 == 0 and diff == 0) or (n % 2 == 1 and diff <= 1):
                break
            if offspring[i] == block_id:
                offspring[i] = flip(offspring[i])
                diff -= 2


def flip(block_id):
    return (block_id + 1) % 2


def search_parent(search_list, total_fitness):
    return bisect.bisect_left(search_list, random.random() * total_fitness)
