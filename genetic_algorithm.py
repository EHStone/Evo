## genetic_algorithm.py
 


######## CODE COPIED FROM WEEK 3 (MAX ONES) ######
##################################################
############### PLACEHOLDER ONLY #################

import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
import fitness as fitness_calc
import cylinder
# import ordered_packing as order
import custom_visualiser as vis


# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

class GeneticAlgorithm:
    def __init__(self, instance: int, population_size: int, order_mutation_rate: float, pos_mutation_rate: float, pos_mutation_dist: float):
        self.instance = instance
        self.all_cylinders = []
        self.population_size = population_size
        self.order_mutation_rate = order_mutation_rate
        self.pos_mutation_rate = pos_mutation_rate
        self.pos_mutation_dist = pos_mutation_dist
        self.population = [] ## matrix with elements [ [ solution[], solution_positions[], and fitness ] [...] [...] ...]
        # self.population_order = []
        # self.population_positions = []
        self.generation = 0
        self.box_x, self.box_y, self.box_w, self.box_h = vis.visualise_container(instance, show_vis=False)
        self.cont_w = instance['container']['width']
        self.cont_h = instance['container']['depth']

        self.best_fitness = 100000
        self.best_solution = None
        self.best_generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        
        for data in instance['cylinders']:
            cyl = cylinder.Cylinder(data['id'], data['diameter'], data['weight'])
            self.all_cylinders.append(cyl)

    def fitness(self, pos = None, genome = None, verbose = False) -> int:
        fitness = 0
        if pos is not None:
            # genome_order = self.population_order[pos]
            # genome_pos = self.population_positions[pos]
            genome_order = self.population[pos][0]
            genome_pos = self.population[pos][1]
        if genome is not None:
            genome_order = genome[0]
            genome_pos = genome[1]
           
        placed_cylinders = []
        iter = 0
        for cyl in genome_order:
            # print(cyl)
            cyl.set_position(genome_pos[iter][0], genome_pos[iter][1])
            # cyl.id = iter
            iter += 1
            placed_cylinders.append(cyl)
        fitness_score, com_X, com_Y = fitness_calc.check_fitness(self.instance, placed_cylinders, verbose)
        fitness += fitness_score
        vis.visualise_container(self.instance, show_vis = verbose, com_x = com_X, com_y = com_Y, placed_cylinders=placed_cylinders)
        # self.population[pos].append(fitness)
        return round(fitness, 2)#, com_X, com_Y
    
    def initialize_population(self) -> None:
        """Initialize population with order and positions"""
        # self.population = []
        for _ in range(self.population_size):
            # genome = self.all_cylinders[:]
            genome = []
            genome_id = []
            for cyl in self.all_cylinders:
                genome.append(cyl)
            random.shuffle(genome)
            for i in genome:
                genome_id.append(i.id)
            # self.population_order.append(genome)
            solution = self.place_cylinders_init(genome)
            # self.population_positions.append(solution)
            self.population.append([genome, solution])

    def place_cylinders_init(self, genome):
        solution = []
        for cyl in genome:
            rand_x = random.uniform(cyl.radius, self.cont_w - cyl.radius)
            rand_y = random.uniform(cyl.radius, self.cont_h - cyl.radius)
                
            # cyl.set_position(rand_x, rand_y)
            solution.append((rand_x, rand_y))

        return solution

    def tournament_selection(self, tournament_size: int = 3) -> List[int]:
        """Select parent using tournament selection"""
        tournament = random.sample(self.population, tournament_size)
        lst_pos = 0 
        best_fitness = 10000000000
        all_fitness = [] ## for testing only
        for i in tournament:
            # fitness = i[2]
            fitness = self.fitness(genome=i)
            # all_fitness.append(fitness) ## For testing only
            if fitness < best_fitness:
                best_genome_pos = lst_pos
                best_fitness = fitness
            lst_pos += 1
        return tournament[best_genome_pos]#, all_fitness ##remove all_fitness when running

    ## modified version of week 5 crossover code 
    def crossover(self, parent1, parent2, parent1_sample_size = 2):
        """
        Alternative implementation of ordered crossover.
        """
        size = len(parent1[0])
        start, end = sorted(random.sample(range(size + 1), parent1_sample_size))
        
        # Copy substring from parent1
        child_order = [None] * size
        child_pos = [None] * size
        child_order[start:end] = parent1[0][start:end]
        child_pos[start:end] = parent1[1][start:end]
        
        # Fill remaining positions with genes from parent2
        parent2_gene_order = []#[gene for gene in parent2[0] if gene not in child_order]
        parent2_gene_pos = []#[gene for gene in parent2[0] if gene not in child_order]
        iter = 0
        for gene in parent2[0]:
            if gene not in child_order:
                parent2_gene_order.append(gene)
                parent2_gene_pos.append(parent2[1][iter])
            iter += 1
        
        # Insert remaining genes
        j = 0
        for i in range(size):
            if child_order[i] is None:
                child_order[i] = parent2_gene_order[j]
                child_pos[i] = parent2_gene_pos[j]
                j += 1
        child = [child_order, child_pos]
        return child
    
    def mutate_order(self, genome):
        """swap mutation with given probability"""
        mutated_order = genome[0].copy()
        mutated_pos = genome[1].copy()
        if random.random() < self.order_mutation_rate:
            pos1 = random.randint(0, len(genome[0])-1)
            pos2 = random.randint(0, len(genome[0])-1)
            while pos2 == pos1:
                pos2 = random.randint(0, len(genome[0])-1)
            mutated_order[pos1] = genome[0][pos2]
            mutated_order[pos2] = genome[0][pos1]
            mutated_pos[pos1] = genome[1][pos2]
            mutated_pos[pos2] = genome[1][pos1]
        mutated = [mutated_order, mutated_pos]
        return mutated
    
    def mutate_pos(self, genome):
        mutated_pos = genome[1].copy()
        for i in range(len(mutated_pos)):
            if random.random() < self.pos_mutation_rate:
                current_x, current_y = mutated_pos[i]

                ## set position shift distance based on a ratio of container size and mutation distance weight value
                x_shift = random.uniform(-self.cont_w * self.pos_mutation_dist, self.cont_w * self.pos_mutation_dist)
                y_shift = random.uniform(-self.cont_h * self.pos_mutation_dist, self.cont_h * self.pos_mutation_dist)

                new_x = current_x + x_shift
                new_y = current_y + y_shift

                new_x = max(genome[0][i].radius, min(self.cont_w - genome[0][i].radius, new_x))
                new_y = max(genome[0][i].radius, min(self.cont_h - genome[0][i].radius, new_y))

                mutated_pos[i] = (new_x, new_y)
        mutated_genome = [genome[0], mutated_pos]
        return mutated_genome
    
    def print_population(self, show_best = False) -> None:
        """Print current population with fitness values"""
        if show_best:
            print(f"\nBest Solution Found in Generation {self.best_generation}:")
            print(f"Best fitness: {self.best_fitness} | Genome: {''.join(map(str, self.best_solution))}")
            self.fitness(genome = self.best_solution, verbose = True)
        else:
            print(f"\nGeneration {self.generation}:")
            fitness_values = [self.fitness(pos) for pos in range(0, len(self.population))] ## change this to counter
            # Sort by fitness (ascending)
            sorted_pop = sorted(zip(self.population, fitness_values), key=lambda x: x[1])
            print(len(self.population))
            print(f"Best fitness: {sorted_pop[0][1]} | Genome: {''.join(map(str, sorted_pop[0][0]))}")
            self.fitness(genome = sorted_pop[0][0], verbose = True)
            print(f"Average fitness: {np.mean(fitness_values):.2f}")
            print(f"Population diversity: {len(set([''.join(map(str, g)) for g in self.population]))} unique genomes")
    
    def run_single_generation(self) -> bool:
        """Run one generation of the GA. Returns True if solution found."""

        # current_fitnesses = [self.fitness(pos) for pos in range(len(self.population))]
        
        # min_fitness = min(current_fitnesses)
        # if min_fitness < self.best_fitness:
        #     xxxxx
        
        current_fitnesses = []
        local_min_fitness = 10000000
        for pos in range(len(self.population)):
            fitness = self.fitness(pos)
            if fitness < local_min_fitness:
                local_min_fitness = fitness
            if fitness < self.best_fitness:
                self.best_fitness = fitness    
                self.best_solution = self.population[pos]     
                self.best_generation = self.generation
            current_fitnesses.append(fitness)

        avg_fitness = np.mean(current_fitnesses)
        self.best_fitness_history.append(local_min_fitness)
        self.avg_fitness_history.append(avg_fitness)

        # Check if we've found the optimal solution
        # min_fitness = min(self.fitness(genome) for genome in self.population)
        min_fitness = min(self.fitness(pos) for pos in range(0, len(self.population)))
        if min_fitness == 0:
            return True
        
        # Create new population
        new_population = []
        
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            # Crossover
            child1 = self.crossover(parent1, parent2)
            
            # Mutation
            child1 = self.mutate_order(child1)
            # child2 = self.mutate(child2)

            child1 = self.mutate_pos(child1)


            new_population.append(child1)
        
        # Keep population size exact
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        return False
    
    def run_until_solution(self, max_generations: int = 1000, verbose: bool = True) -> int:
        """Run GA until solution is found or max generations reached"""
        self.generation = 0
        self.initialize_population()

        # if verbose:
        #     self.print_population()
        
        while self.generation < max_generations:
            if self.run_single_generation():
                if verbose:
                    self.print_population()
                    print(f"\n*** SOLUTION FOUND in {self.generation} generations! ***")
                    self.plot_fitness_graph() # Plot even if solution not found
                return self.generation
            
            # if verbose and (self.generation % 100 == 0 or self.generation < 5):
            #     self.print_population()


        if verbose:
            self.print_population(show_best = True)
            print(f"\nMax generations ({max_generations}) reached without finding solution.")

            self.plot_fitness_graph() # Plot even if solution not found
        return max_generations
    
    def plot_fitness_graph(self):
        """Generates a graph of fitness progression"""
        plt.figure(figsize=(10, 6))
        plt.plot(self.best_fitness_history, label='Best Fitness', color='blue', linewidth=2)
        plt.plot(self.avg_fitness_history, label='Average Fitness', color='orange', linestyle='--', alpha=0.7)
        
        plt.title(f'Fitness Progression (Generation {self.generation})')
        plt.xlabel('Generation')
        plt.ylabel('Fitness Score')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()


    
    