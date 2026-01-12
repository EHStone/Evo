import greedy_baseline as baseline
import container_instances as inst
import container_impossible_instances as imposs_inst
import genetic_algorithm as genAlgo

all_instances = inst.generate_all_instances(False)
basic_instances = all_instances['basic_instances']
# advanced_instances = all_instances['challenging_instances']

impossible_instances_all = imposs_inst.generate_impossible_instances(False)
impossible_instances = impossible_instances_all['impossible_instances']

# for instance in basic_instances:
#     baseline.run_baseline(instance)

# for instance in advanced_instances:
#     baseline.run_baseline(instance)

# print("WARNING: IMPOSSIBLE INSTANCES BEING TESTED.")
# for instance in impossible_instances:
#     baseline.run_baseline(instance)

inst_iter = 1
for instance in basic_instances:
    # if len(instance['cylinders']) > 4: ## use instance with more cylinders to test crossover
    print("Running Basic instance number ", inst_iter)
    inst_iter += 1
    ga = genAlgo.GeneticAlgorithm(instance, population_size = 100, order_mutation_rate = .1, pos_mutation_rate = 0.15, pos_mutation_dist = 0.05)
    generations_needed = ga.run_until_solution(verbose=True)
    # break
    