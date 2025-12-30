## genetic_algorithm.py
 


######## CODE COPIED FROM WEEK 3 (MAX ONES) ######
##################################################
############### PLACEHOLDER ONLY #################

import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
import fitness

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

class GeneticAlgorithm:
    def __init__(self, string_length: int, population_size: int, mutation_rate: float):
        self.string_length = string_length
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = []
        self.generation = 0
    
    def fitness(self, genome: List[int]) -> int:
        """Fitness function: count the number of 1s in the binary string"""
        return sum(genome)
    
    def initialize_population(self) -> None:
        """Initialize population with random binary strings"""
        self.population = []
        for _ in range(self.population_size):
            genome = [random.randint(0, 1) for _ in range(self.string_length)]
            self.population.append(genome)
    
    def tournament_selection(self, tournament_size: int = 3) -> List[int]:
        """Select parent using tournament selection"""
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=self.fitness)
    
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
        fitness_values = [self.fitness(genome) for genome in self.population]
        
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
        
        if verbose:
            self.print_population()
        
        while self.generation < max_generations:
            if self.run_single_generation():
                if verbose:
                    self.print_population()
                    print(f"\n*** SOLUTION FOUND in {self.generation} generations! ***")
                return self.generation
            
            if verbose and (self.generation % 10 == 0 or self.generation < 5):
                self.print_population()
        
        if verbose:
            print(f"\nMax generations ({max_generations}) reached without finding solution.")
        return max_generations
    
    