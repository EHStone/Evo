import custom_visualiser as vis
import container_instances as inst
import fitness
import numpy as np
import random

# ## Fetch instances from provided file and test visualiser
# all_instances = inst.generate_all_instances(False)
# basic_instances = all_instances['basic_instances']

# ## Visualise container and fetch center 60% dimensions / co-ords
# current_inst = basic_instances[0] 



class Cylinder:
    def __init__(self, id, diameter, weight):
        self.id = id
        self.diameter = diameter
        self.radius = diameter / 2.0
        self.weight = weight
        self.x = 0
        self.y = 0
        self.color = (random.random(), random.random(), random.random()) # For visualisation

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def overlaps(self, other):
        dist = self.distance_to(other)
        # Check if distance is less than sum of radii (with slight buffer)
        return dist < (self.radius + other.radius + 0.05) 


def run_baseline(current_inst):

    box_x, box_y, box_w, box_h = vis.visualise_container(current_inst, show_vis=False)
    center_point = (box_x+box_w/2, box_y+box_h/2)


    placed_cylinders = [] # Keep track of what we successfully placed
    total_weight = 0
    check_first_placed = 1 

    # Container Boundaries
    cont_w = current_inst['container']['width']
    cont_h = current_inst['container']['depth']

    # print(f"--- Processing Container ({cont_w}x{cont_h}) ---")

    for data in current_inst['cylinders']:
        
        cyl = Cylinder(data['id'], data['diameter'], data['weight'])

        ## check if adding will result in overweight
        if (total_weight + cyl.weight) > current_inst['container']['max_weight']:
            # print(f"Skipping Cylinder {cyl.id}: Max weight exceeded.")
            continue
        
        placed = False
        
        ## if checked cylinder is the first to be placed, place in center
        if check_first_placed == 1:
            cyl.set_position(center_point[0], center_point[1])
            placed_cylinders.append(cyl)
            total_weight += cyl.weight
            check_first_placed = 0
            placed = True
            # print(f"Placed Cylinder {cyl.id} (First) at Center")
            
        else:
            max_attempts = 1000 
            
            for _ in range(max_attempts):
                rand_x = random.uniform(cyl.radius, cont_w - cyl.radius)
                rand_y = random.uniform(cyl.radius, cont_h - cyl.radius)
                
                cyl.set_position(rand_x, rand_y)
                
                collision = False
                for other_cyl in placed_cylinders:
                    if cyl.overlaps(other_cyl):
                        collision = True
                        break 
                
                if not collision:
                    placed_cylinders.append(cyl)
                    total_weight += cyl.weight
                    placed = True
                    # print(f"Placed Cylinder {cyl.id} at ({rand_x:.2f}, {rand_y:.2f})")
                    break 
            
            # if not placed:
                # print(f"Could not place Cylinder {cyl.id} after {max_attempts} attempts.")

    fitness_score, com_X, com_Y = fitness.check_fitness(current_inst, placed_cylinders)
    vis.visualise_container(current_inst, com_x = com_X, com_y = com_Y, placed_cylinders=placed_cylinders)

