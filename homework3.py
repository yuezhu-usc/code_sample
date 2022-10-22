# Name: Yue Zhu
# USC ID: 1260841401
# Date: Sept-21-2022
#
# 3D Travelling Salesman Problem using Genetic Algorithm
#
# Overview of GA Cycle:
# Create randomized initial population (300) -> Enter Cycle:
#   Fitness: New population -> find, rank, sort their fitness level ( 1 / total_distance)^2
#   Selection: Roulette wheel selection based on each fitness level and Elitism for top 50 routes
#   Crossover: Ordered crossover and each selected route will be randomly paired to another
#   Mutation: Dynamic Swapping Mutation according to each route's fitness relative to average and max fitness
#   Cataclysm: Kill n% population and add newly randomized population when fitness average is close to max
#   Repeat Cycle

import math
import random


# Calculate Euclidean distance between two cities (x, y, z)
def calculate_distance(city1, city2):
    return math.sqrt(math.pow(city1.x - city2.x, 2) + math.pow(city1.y - city2.y, 2)
                     + math.pow(city1.z - city2.z, 2))


# A Class that records the x, y, z coordinates of the input
class City:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


# A Class that contains an array of the travelling salesman route, a calculated distance, and a fitness
class Route:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0

    # Calculate distance of each city
    def find_distance(self):
        route_length = len(self.route)
        route_distance = 0

        for i in range(route_length):
            start_pos = self.route[i]
            end_pos = self.route[i + 1] if i + 1 < route_length else self.route[0]
            route_distance += calculate_distance(start_pos, end_pos)
        self.distance = route_distance
        return self.distance

    # Calculate fitness as power of 2
    def find_fitness(self):
        self.fitness = math.pow(1.0 / self.find_distance(), 2)
        return self.fitness


# Read input.txt
def read_input():
    city_list = []
    file = open('input.txt', 'r')
    num_of_cities = file.readline()
    city = file.readline()
    while city:
        pos = [int(i) for i in city.split() if i.isdigit()]
        city_list.append(City(pos[0], pos[1], pos[2]))
        city = file.readline()
    return city_list


# Create initial_population randomly
def create_population(city_list, population_size):
    population_list = []
    city_length = len(city_list)
    for i in range(population_size):
        population_list.append(random.sample(city_list, city_length))
    return population_list


# Rank population based on their travelling distance
def rank_fitness(population_list):
    fitness_dict = {}
    population_length = len(population_list)

    # fitness_dict = {'i', 'fitness ranking'}
    for i in range(population_length):
        route = Route(population_list[i])
        fitness_dict[i] = route.find_fitness()

    # return sorted fitness
    return sorted(fitness_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)


# Select mating group based on roulette wheel-based and create the list
# Also calculate average fitness and maximum fitness
def generate_matingpool(fitness_dict, priority_size):
    # Find the sum of fitness
    # Calculate chance dict['id'] = {[lower bound, upper bound}}
    selection_list = []
    roulette_dict = {}
    fitness_sum = 0
    fitness_average = 0
    fitness_maximum = fitness_dict[0][1]
    population_length = len(fitness_dict)

    # Calculate the sum of fitness
    for i in range(population_length):
        roulette_dict[i] = [fitness_sum, fitness_sum + fitness_dict[i][1]]
        fitness_sum += fitness_dict[i][1]

    fitness_average = fitness_sum / population_length

    # Append priority group
    for i in range(0, priority_size):
        selection_list.append([fitness_dict[i][0], fitness_dict[i][1]])

    # Randomly select mating group according to fitness probability
    for i in range(priority_size, population_length - priority_size):
        select_num = random.uniform(0.0, fitness_sum)
        for j in range(population_length):
            if roulette_dict[j][0] <= select_num <= roulette_dict[j][1]:
                selection_list.append([fitness_dict[j][0], fitness_dict[j][1]])

    return selection_list, fitness_average, fitness_maximum


# Crossover the parents and return the child
def crossover(parent1, parent2, start_index, end_index):
    if start_index > end_index:
        return crossover(parent1, parent2, end_index, start_index)

    child = []
    child1 = []
    child2 = []
    length = len(parent1)

    # Get child1 from parent 1
    for i in range(start_index, end_index + 1):
        child1.append(parent1[i])

    # Get child2 from parent 2
    for i in range(length):
        if parent2[i] not in child1:
            child2.append(parent2[i])

    # Merge two children
    child1ptr = 0
    child2ptr = 0
    for i in range(length):
        if start_index <= i <= end_index:
            child.append(child1[child1ptr])
            child1ptr += 1
        else:
            child.append(child2[child2ptr])
            child2ptr += 1

    return child


# Crossover the mating pool and create the next
def create_crossover(population_list, mating_list, priority_size):
    crossover_list = []
    population_size = len(population_list)
    city_size = len(population_list[0])
    crossover_pool = random.sample(mating_list, population_size - priority_size)

    # Priority routes will skip to next generation
    for i in range(priority_size):
        crossover_list.append([population_list[mating_list[i][0]], mating_list[i][1]])

    # Each other route will be randomly pair to another route for crossover
    for i in range(population_size - priority_size):
        parent1 = population_list[crossover_pool[i][0]]
        parent2 = population_list[crossover_pool[random.randint(0, len(crossover_pool) - 1)][0]]
        start_index = random.randint(0, city_size - 1)
        end_index = random.randint(0, city_size - 1)
        child = crossover(parent1, parent2, start_index, end_index)
        crossover_list.append([child, mating_list[i][1]])

    return crossover_list


# Invoke mutation on random population
# Dynamic Mutation: https://aip.scitation.org/doi/pdf/10.1063/1.5039131
def invoke_mutation(crossover_list, max_mutation_rate, min_mutation_rate, fitness_average, fitness_maximum):
    mutation_list = []
    population_size = len(crossover_list)
    city_size = len(crossover_list[0][0])
    mutation_rate = 0

    for i in range(population_size):
        fitness_curr = crossover_list[i][1]
        # Dynamic Mutation according to the formula in the link above
        if fitness_curr >= fitness_average:
            mutation_rate = max_mutation_rate * (max_mutation_rate - min_mutation_rate) * \
                            (fitness_curr - fitness_average) / (fitness_maximum - fitness_average)
        else:
            mutation_rate = max_mutation_rate

        for city1 in range(city_size):
            if random.random() < mutation_rate:
                city2 = random.randint(0, city_size - 1)

                temp = crossover_list[i][0][city1]
                crossover_list[i][0][city1] = crossover_list[i][0][city2]
                crossover_list[i][0][city2] = temp

        mutation_list.append(crossover_list[i][0])
    return mutation_list


# Start Cataclysm, create fresh new salespeople if it looks like reaching a local minimum
def start_cataclysm(city_list, mutation_list, cataclysm_rate, cataclysm_percentage):
    new_population = []
    population_size = len(mutation_list)
    old_population_size = math.ceil(population_size - population_size * cataclysm_percentage)
    new_population_size = population_size - old_population_size

    if random.random() < cataclysm_rate:
        old_population_list = random.sample(mutation_list, old_population_size)
        new_population_list = create_population(city_list, new_population_size)
        new_population = old_population_list + new_population_list
    else:
        new_population = mutation_list

    return new_population


# Simulate one generation and return the new population
def simulate_cycle(city_list, population_list, priority_size, max_mutation_rate, min_mutation_rate, cataclysm_rate,
                   cataclysm_percentage):
    # Calculate, rank, and sort the fitness level according to each route's distance
    fitness_dict = rank_fitness(population_list)
    # Generate a mating list based on roulette wheel-based selection
    mating_list, fitness_average, fitness_maximum = generate_matingpool(fitness_dict, priority_size)
    # Crossover the mating pool and create the post-crossover list
    crossover_list = create_crossover(population_list, mating_list, priority_size)
    # Invoke mutation on random crossover
    new_population = invoke_mutation(crossover_list, max_mutation_rate, min_mutation_rate, fitness_average,
                                     fitness_maximum)
    # Start Cataclysm, create fresh new salespeople if it looks like reaching a local minimum
    if random.random() < fitness_average / fitness_maximum:
        new_population = start_cataclysm(city_list, new_population, cataclysm_rate, cataclysm_percentage)

    return new_population


# Write output.txt
def write_output(route_list):
    file = open('output.txt', 'w')

    for i in range(len(route_list)):
        city = route_list[i]
        string = str(city.x) + " " + str(city.y) + " " + str(city.z) + "\n"
        file.write(string)

    # Write back to original city
    file.write(str(route_list[0].x) + " " + str(route_list[0].y) + " " + str(route_list[0].z))
    file.close()


# Main Function
def genetic_algorithm(population_size, generation_size, priority_size, max_mutation_rate, min_mutation_rate,
                      cataclysm_rate, cataclysm_percentage):
    # Read input.txt and construct an array of all cities
    city_list = read_input()
    # Create initial_population list with city_list
    population_list = create_population(city_list, population_size)

    # Start simulation util generation_size
    for i in range(generation_size):
        population_list = simulate_cycle(city_list, population_list, priority_size, max_mutation_rate,
                                         min_mutation_rate,
                                         cataclysm_rate, cataclysm_percentage)

    # Write output.txt
    final = rank_fitness(population_list)
    route = population_list[final[0][0]]
    write_output(route)


if __name__ == '__main__':
    genetic_algorithm(300, 700, 40, 0.02, 0.01, 0.03, 0.4)
