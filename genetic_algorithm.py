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
    def __init__(self, instance: int, population_size: int, mutation_rate: float):
        self.instance = instance
        self.all_cylinders = []
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [] ## matrix with elements [ [ solution[], solution_positions[], and fitness ] [...] [...] ...]
        self.population_order = []
        self.population_positions = []
        self.generation = 0
        self.box_x, self.box_y, self.box_w, self.box_h = vis.visualise_container(instance, show_vis=False)
        self.cont_w = instance['container']['width']
        self.cont_h = instance['container']['depth']
        
        for data in instance['cylinders']:
            cyl = cylinder.Cylinder(data['id'], data['diameter'], data['weight'])
            self.all_cylinders.append(cyl)

    def fitness(self, pos) -> int:
        fitness = 0
        genome_order = self.population_order[pos]
        genome_pos = self.population_positions[pos]

        placed_cylinders = []
        iter = 0
        for cyl in genome_order:
            # print(cyl)
            cyl.set_position(genome_pos[iter][0], genome_pos[iter][1])
            cyl.id = iter
            iter += 1
            placed_cylinders.append(cyl)
        fitness_score, com_X, com_Y = fitness_calc.check_fitness(self.instance, placed_cylinders)
        fitness += fitness_score
        vis.visualise_container(self.instance, show_vis = False, com_x = com_X, com_y = com_Y, placed_cylinders=placed_cylinders)
        self.population[pos].append(fitness)
        return fitness, com_X, com_Y
    
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
            self.population_order.append(genome)
            solution = self.place_cylinders_init(genome)
            self.population_positions.append(solution)
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
        best_fitness = 1000
        all_fitness = []
        for i in tournament:
            fitness = i[2]
            all_fitness.append(fitness)
            if fitness < best_fitness:
                best_genome_pos = lst_pos
                best_fitness = fitness
            lst_pos += 1
        return tournament[best_genome_pos], all_fitness
    

    ##---------------------------------------------------------------------------##

    
    def crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """Single-point crossover"""
        if len(parent1) <= 1:
            return parent1.copy(), parent2.copy()
        
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    
    def mutate(self, genome: List[int]) -> List[int]:
        """Bit-flip mutation with given probability"""
        mutated = genome.copy()
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = 1 - mutated[i]  # Flip bit
        return mutated
    
    def print_population(self) -> None:
        """Print current population with fitness values"""
        print(f"\nGeneration {self.generation}:")
        fitness_values = [self.fitness(genome) for genome in self.population] ## change this to counter
        
        # Sort by fitness (descending)
        sorted_pop = sorted(zip(self.population, fitness_values), key=lambda x: x[1], reverse=True)
        
        print(f"Best fitness: {sorted_pop[0][1]} | Genome: {''.join(map(str, sorted_pop[0][0]))}")
        print(f"Average fitness: {np.mean(fitness_values):.2f}")
        print(f"Population diversity: {len(set([''.join(map(str, g)) for g in self.population]))} unique genomes")
    
    def run_single_generation(self) -> bool:
        """Run one generation of the GA. Returns True if solution found."""
        # Check if we've found the optimal solution
        max_fitness = max(self.fitness(genome) for genome in self.population)
        if max_fitness == self.string_length:
            return True
        
        # Create new population
        new_population = []
        
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            # Crossover
            child1, child2 = self.crossover(parent1, parent2)
            
            # Mutation
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            new_population.extend([child1, child2])
        
        # Keep population size exact
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        return False
    
    def run_until_solution(self, max_generations: int = 1000, verbose: bool = True) -> int:
        """Run GA until solution is found or max generations reached"""
        self.generation = 0
        self.initialize_population()
        fitness_values = [self.fitness(pos) for pos in range(0, len(self.population_order))] ## change this to counter
        print(self.tournament_selection(tournament_size=3)) ## Test tournament selection
        # if verbose:
        #     self.print_population()
        
        # while self.generation < max_generations:
        #     if self.run_single_generation():
        #         if verbose:
        #             self.print_population()
        #             print(f"\n*** SOLUTION FOUND in {self.generation} generations! ***")
        #         return self.generation
            
        #     if verbose and (self.generation % 10 == 0 or self.generation < 5):
        #         self.print_population()
        
        # if verbose:
        #     print(f"\nMax generations ({max_generations}) reached without finding solution.")
        return max_generations


    
    