import matplotlib.pyplot as plt
import numpy as np
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


# def test_algorithm_performance(baseline, mhd, instances_dict, iterations=1):
#     """
#     Runs baseline and mhd algorithms across multiple instance categories.
    
#     Args:
#         baseline: The baseline algorithm object/module.
#         mhd: The mhd algorithm object/module.
#         instances_dict: A dictionary where keys are category names and values are lists of instances.
#         iterations: Number of times to run each instance (for stochastic algorithms).
#     """
#     results = {
#         "baseline": {cat: {"success": 0, "total": 0} for cat in instances_dict},
#         "mhd": {cat: {"success": 0, "total": 0} for cat in instances_dict}
#     }

#     # Execution Loop
#     for category, instances in instances_dict.items():
#         if category == "impossible":
#             print(f"--- WARNING: Testing {len(instances)} IMPOSSIBLE instances ---")
        
#         for instance in instances:
#             for _ in range(iterations):
#                 # Test Baseline
#                 if baseline.run_baseline(instance, verbose=False):
#                     results["baseline"][category]["success"] += 1
#                 results["baseline"][category]["total"] += 1
                
#                 # Test MHD
#                 if mhd.run_mhd(instance, verbose=False):
#                     results["mhd"][category]["success"] += 1
#                 results["mhd"][category]["total"] += 1

#     # Printing Success Rates
#     print("\n--- PERFORMANCE SUMMARY ---")
#     for algo in ["baseline", "mhd"]:
#         print(f"\nAlgorithm: {algo.upper()}")
#         for category in instances_dict:
#             res = results[algo][category]
#             rate = (res["success"] / res["total"]) * 100 if res["total"] > 0 else 0
#             print(f"  {category.capitalize()}: {rate:.2f}% ({res['success']}/{res['total']})")

#     # Plotting results
#     plot_comparison(results, instances_dict.keys())

# def plot_comparison(results, categories):
#     categories = [c.capitalize() for c in categories]
#     baseline_rates = [
#         (results["baseline"][c.lower()]["success"] / results["baseline"][c.lower()]["total"]) * 100 
#         for c in categories
#     ]
#     mhd_rates = [
#         (results["mhd"][c.lower()]["success"] / results["mhd"][c.lower()]["total"]) * 100 
#         for c in categories
#     ]

#     x = np.arange(len(categories))
#     width = 0.35

#     fig, ax = plt.subplots(figsize=(10, 6))
#     ax.bar(x - width/2, baseline_rates, width, label='Baseline', color='#3498db')
#     ax.bar(x + width/2, mhd_rates, width, label='MHD', color='#e74c3c')

#     ax.set_ylabel('Success Rate (%)')
#     ax.set_title('Algorithm Success Rate Comparison')
#     ax.set_xticks(x)
#     ax.set_xticklabels(categories)
#     ax.set_ylim(0, 100)
#     ax.legend()
    
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
#     plt.tight_layout()
#     plt.show()

# # Example usage:
# instances = {
#     "basic": basic_instances,
#     "advanced": advanced_instances,
#     "impossible": impossible_instances
# }
# test_algorithm_performance(baseline, mhd, instances)





import matplotlib.pyplot as plt
import numpy as np

def test_detailed_performance(baseline, mhd, instances_dict, iterations=100):
    """
    Runs algorithms multiple times per instance and reports per-instance success rates.
    """
    # detailed_results stores: { category: [ { 'instance_id': 0, 'baseline_rate': 0.8, 'mhd_rate': 1.0 }, ... ] }
    detailed_results = {cat: [] for cat in instances_dict}

    for category, instances in instances_dict.items():
        print(f"Testing category: {category.upper()}...")
        
        for idx, instance in enumerate(instances):
            b_successes = 0
            m_successes = 0
            ga_successes = 0
            
            all_fitness_rand = []
            successful_fitness_rand = []
            all_fitness_mhd = []
            successful_fitness_mhd = []
            all_fitness_ga = []
            successful_fitness_ga = []
            for _ in range(iterations):
                # Run Baseline
                success_rand, fitness_rand = baseline.run_baseline(instance, verbose=False)
                all_fitness_rand.append(fitness_rand)
                success_mhd, fitness_mhd = mhd.run_mhd(instance, verbose=False)
                all_fitness_mhd.append(fitness_mhd)
                success_mhd, fitness_mhd = mhd.run_mhd(instance, verbose=False)
                all_fitness_mhd.append(fitness_mhd)
                ga = genAlgo.GeneticAlgorithm(instance, population_size = 100, order_mutation_rate = .1, pos_mutation_rate = 0.15, pos_mutation_dist = 0.05)
                _, success_ga, fitness_ga = ga.run_until_solution(max_generations=1000, verbose=False)
                all_fitness_ga.append(fitness_ga)

                if success_rand:
                    b_successes += 1
                    successful_fitness_rand.append(fitness_rand)
                # Run MHD
                if success_mhd:
                    m_successes += 1
                    successful_fitness_mhd.append(fitness_mhd)
                if success_ga:
                    ga_successes += 1
                    successful_fitness_ga.append(fitness_ga)
            # Helper for safe averaging
            avg = lambda x: sum(x) / len(x) if len(x) > 0 else 0.0

            detailed_results[category].append({
                "id": f"{category[:3]}_{idx}",
                "b_rate": (b_successes / iterations) * 100,
                "m_rate": (m_successes / iterations) * 100,
                "b_avg_fit": avg(all_fitness_rand),
                "m_avg_fit": avg(all_fitness_mhd),
                "b_succ_fit": avg(successful_fitness_rand),
                "m_succ_fit": avg(successful_fitness_mhd),
                "ga_rate": (ga_successes / iterations) * 100,
                "ga_avg_fit": avg(all_fitness_ga),
                "ga_succ_fit": avg(successful_fitness_ga),
            })

    # Print Detailed Text Report
    header = f"{'INSTANCE':<10} | {'B-SUCC %':<10} | {'M-SUCC %':<10}| {'GA-SUCC %':<10}  | {'B-AVG FIT':<10} | {'B-SUCC FIT':<10} | {'M-AVG FIT':<10} | {'M-SUCC FIT':<10} | {'GA-AVG FIT':<10}"
    print(f"\n{header}")
    print("-" * len(header))
    for category, reports in detailed_results.items():
        for r in reports:
            print(f"{r['id']:<10} | {r['b_rate']:>8.1f}% | {r['m_rate']:>8.1f}% | {r['ga_rate']:>8.1f}% | {r['b_avg_fit']:>10.2f} | {r['b_succ_fit']:>10.2f} | {r['m_avg_fit']:>10.2f} | {r['m_succ_fit']:>10.2f} | {r['ga_avg_fit']:>10.2f} ")

    plot_fitness_comparison(detailed_results)

def plot_fitness_comparison(detailed_results):
    all_labels, b_fit, m_fit = [], [], []
    
    for category, reports in detailed_results.items():
        for r in reports:
            all_labels.append(r['id'])
            b_fit.append(r['b_avg_fit'])
            m_fit.append(r['m_avg_fit'])

    x = np.arange(len(all_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, b_fit, width, label='Baseline Avg Fitness', color='#3498db')
    ax.bar(x + width/2, m_fit, width, label='MHD Avg Fitness', color='#e74c3c')

    ax.set_ylabel('Fitness Value')
    ax.set_title('Overall Average Fitness Comparison per Instance')
    ax.set_xticks(x)
    ax.set_xticklabels(all_labels, rotation=45)
    ax.legend()
    
    plt.tight_layout()
    plt.show()

# Example usage:
instances = {"basic": basic_instances, "advanced": advanced_instances, "impossible": impossible_instances}
test_detailed_performance(baseline, mhd, instances, iterations=100)