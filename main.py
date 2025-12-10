import greedy_baseline as baseline
import container_instances as inst

all_instances = inst.generate_all_instances(False)
basic_instances = all_instances['basic_instances']
advanced_instances = all_instances['challenging_instances']
for instance in basic_instances:
    baseline.run_baseline(instance)

for instance in advanced_instances:
    baseline.run_baseline(instance)