import bisect
import logging
import random
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
    offsprings = crossover(parents)
    for offspring in offsprings:
        mutation(offspring)
    replace_with_offsprings(circuit, population, fitness_list, offsprings)

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
    mincut, count, best = -1, 0, None
    for chromeosome in population:
        if mincut < 0 or chromeosome.mincut < mincut:
            mincut = chromeosome.mincut
            count = 0
            best = chromeosome
        if mincut == chromeosome.mincut:
            count += 1
    logging.info("mincut: {} | rate: {:.2%}".format(best.mincut, count / 50))
    return (count / 50) >= 0.8, best


def replace_with_offsprings(circuit, population, fitness_list, offsprings):
    victims = find_victims(fitness_list)
    for i, v in enumerate(victims):
        data = init_partition(circuit, offsprings[i])
        kl_inner(circuit, data, None, True)
        population[v] = data


def random_population(circuit: Circuit):
    k = 50
    popultation = [init_partition(circuit) for _ in range(k)]
    return popultation


def select_parent(population):
    fitness_list, total_fitness, search_list = calculate_fitness(population)

    parents = [search_parent(population, search_list, total_fitness),
               search_parent(population, search_list, total_fitness)]

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
        fitness = (worst_cutsize - chromeosome.mincut) + (worst_cutsize - best_cutsize) // 3
        fitness_list.append(fitness)
        total_fitness += fitness
        search_list.append(total_fitness)

    return fitness_list, total_fitness, search_list


def crossover(parents):
    # 5-point crossover
    k = 5
    parent1 = parents[0].nodes_block_id
    parent2 = parents[1].nodes_block_id
    n = len(parent1)  # cell size
    crossover_points = sorted(random.sample(range(n), k))

    offspring1, offspring2 = [], []
    j = 0
    for i in range(n):
        if j % 2 == 0:
            offspring1.append(parent1[i])
            offspring2.append(parent1[i])
        else:
            offspring1.append(parent2[i])
            offspring2.append(flip(parent2[i]))
        if j < k and i == crossover_points[j]:
            j += 1

    return offspring1, offspring2


def find_victims(fitness_list):
    min1, min2 = -1, -1
    for i, v in enumerate(fitness_list):
        if min1 < -1 or v < fitness_list[min1]:
            min1 = i
        elif min2 < -1 or v < fitness_list[min2]:
            min2 = i
    return min1, min2


def mutation(offspring):
    n = len(offspring)
    m = random.randint(0, n // 100)
    for _ in range(m):
        i = random.randrange(0, n)
        offspring[i] = flip(offspring[i])

    # balance
    diff = reduce(lambda a, b: a + (1 if b == 1 else -1), offspring, 0)

    for i in random.sample(range(n), n):
        if (n % 2 == 0 and diff == 0) or (n % 2 == 1 and abs(diff) <= 1):
            break
        if diff > 0 and offspring[i] == 1:
            offspring[i] = flip(offspring[i])
            diff -= 2
        elif diff < 0 and offspring[i] == 0:
            offspring[i] = flip(offspring[i])
            diff += 2


def flip(block_id):
    return (block_id + 1) % 2


def search_parent(population, search_list, total_fitness):
    return population[bisect.bisect_left(search_list, random.random() * total_fitness)]
