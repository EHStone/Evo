import greedy_baseline as baseline
import container_instances as inst
import container_impossible_instances as imposs_inst
import genetic_algorithm as genAlgo
import mhd
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools

all_instances = inst.generate_all_instances(False)
basic_instances = all_instances['basic_instances']
advanced_instances = all_instances['challenging_instances']

impossible_instances_all = imposs_inst.generate_impossible_instances(False)
impossible_instances = impossible_instances_all['impossible_instances']

# # for instance in basic_instances:
# #     baseline.run_baseline(instance)

# # for instance in advanced_instances:
# #     baseline.run_baseline(instance)

# # print("WARNING: IMPOSSIBLE INSTANCES BEING TESTED.")
# # for instance in impossible_instances:
# #     baseline.run_baseline(instance)

# # for instance in basic_instances:
# #     mhd.run_mhd(instance)
# # for instance in advanced_instances:
# #     mhd.run_mhd(instance)
# # for instance in impossible_instances:
# #     mhd.run_mhd(instance)

# inst_iter = 1
# for instance in basic_instances:
#     # if len(instance['cylinders']) > 4: ## use instance with more cylinders to test crossover
#     print("Running Basic instance number ", inst_iter)
#     inst_iter += 1
#     ga = genAlgo.GeneticAlgorithm(instance, population_size = 100, order_mutation_rate = .1, pos_mutation_rate = 0.15, pos_mutation_dist = 0.05)
#     generations_needed = ga.run_until_solution(verbose=True)

# inst_iter = 1
# for instance in advanced_instances:
#     # if len(instance['cylinders']) > 4: ## use instance with more cylinders to test crossover
#     print("Running Advanced instance number ", inst_iter)
#     inst_iter += 1
#     ga = genAlgo.GeneticAlgorithm(instance, population_size = 100, order_mutation_rate = .1, pos_mutation_rate = 0.15, pos_mutation_dist = 0.05)
#     generations_needed = ga.run_until_solution(verbose=True)

# inst_iter = 1
# for instance in impossible_instances:
#     # if len(instance['cylinders']) > 4: ## use instance with more cylinders to test crossover
#     print("Running Impossible instance number ", inst_iter)
#     inst_iter += 1
#     ga = genAlgo.GeneticAlgorithm(instance, population_size = 100, order_mutation_rate = .1, pos_mutation_rate = 0.15, pos_mutation_dist = 0.05)
#     generations_needed = ga.run_until_solution(verbose=True)

# --- 1. Configuration & Setup ---

# Group your instances to make looping cleaner
all_datasets = {
    "Basic": basic_instances,
    "Advanced": advanced_instances#,
    # "Impossible": impossible_instances
}

# Define the hyperparameter values you want to test
# Be careful: The number of total runs is multiplicative!
param_grid = {
    "population_size": [75, 100, 125],
    "order_mutation_rate": [0.025, 0.05, 0.075, 0.1],
    "pos_mutation_rate": [0.001, 0.01, 0.05, 0.1],
    "pos_mutation_dist": [.01, 0.05, .1, .15, .25] 
}

results = []

# Generate all combinations of parameters
keys, values = zip(*param_grid.items())
param_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

print(f"Total configurations to test per instance: {len(param_combinations)}")

# --- 2. Execution Loop ---

for dataset_name, instances in all_datasets.items():
    print(f"--- Processing {dataset_name} Instances ---")
    
    for i, instance in enumerate(instances):
        # Optional: Original filter logic
        # if len(instance['cylinders']) <= 4: continue

        for params in param_combinations:
            # Feedback to console
            print(f"[{dataset_name} Inst {i+1}] Testing params: {params}")

            # Initialize GA with current parameter set
            ga = genAlgo.GeneticAlgorithm(
                instance, 
                population_size=params['population_size'], 
                order_mutation_rate=params['order_mutation_rate'], 
                pos_mutation_rate=params['pos_mutation_rate'], 
                pos_mutation_dist=params['pos_mutation_dist']
            )
            
            # Run the algorithm
            # Note: verbose=False is recommended to prevent console flooding during grid search
            generations_needed = ga.run_until_solution(max_generations = 100, verbose=False)

            # Store the data
            record = {
                "Dataset": dataset_name,
                "Instance_ID": i,
                "Generations": generations_needed,
                **params # Unpacks the current parameters into the record
            }
            results.append(record)

# --- 3. Data Processing & Visualization ---

# Convert list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(results)

# Print a summary of the best results
print("\n--- Top 5 Fastest Configurations ---")
print(df.sort_values(by="Generations").head(5))

# Set the visual style
sns.set_theme(style="whitegrid")

# Visualization 1: Impact of Population Size on Generations (grouped by Dataset)
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="population_size", y="Generations", hue="Dataset")
plt.title("Performance Distribution by Population Size")
plt.ylabel("Generations Needed")
plt.show()

# Visualization 2: Interaction between Mutation Rates (Heatmap)
# We aggregate by mean to see general trends
pivot_table = df.pivot_table(
    values="Generations", 
    index="order_mutation_rate", 
    columns="pos_mutation_rate", 
    aggfunc="mean"
)

plt.figure(figsize=(8, 6))
sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="viridis_r")
plt.title("Average Generations: Order vs Position Mutation Rate")
plt.show()

# Visualization 3: Detailed Line Plot (Performance across parameters)
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x="order_mutation_rate", y="Generations", hue="Dataset", style="population_size", markers=True)
plt.title("Impact of Order Mutation Rate across Datasets and Pop Sizes")
plt.show()

# Visualization 4: Effect of Position Mutation Distance
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=df, 
    x="pos_mutation_dist", 
    y="Generations", 
    hue="Dataset", 
    marker="o"
)
plt.title("Impact of Position Mutation Distance on Convergence Speed")
plt.xlabel("Position Mutation Distance")
plt.ylabel("Generations Needed (Lower is Better)")
plt.show()

pivot_pos = df.pivot_table(
    values="Generations", 
    index="pos_mutation_dist", 
    columns="pos_mutation_rate", 
    aggfunc="mean"
)

plt.figure(figsize=(8, 6))
sns.heatmap(pivot_pos, annot=True, fmt=".1f", cmap="viridis_r")
plt.title("Avg Generations: Mutation Distance vs. Rate")
plt.ylabel("Mutation Distance (Magnitude)")
plt.xlabel("Mutation Rate (Probability)")
plt.show()