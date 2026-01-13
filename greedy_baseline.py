import custom_visualiser as vis
# import container_instances as inst
import ordered_packing as order
import fitness
import cylinder
import numpy as np
import random

def run_baseline(current_inst):

    box_x, box_y, box_w, box_h = vis.visualise_container(current_inst, show_vis=False)
    center_point = (box_x+box_w/2, box_y+box_h/2)


    placed_cylinders = [] # Keep track of what we successfully placed
    total_weight = 0
    check_first_placed = 1 

    # Container Boundaries
    cont_w = current_inst['container']['width']
    cont_h = current_inst['container']['depth']
    total_attempts = 0
    # print(f"--- Processing Container ({cont_w}x{cont_h}) ---")

    for data in current_inst['cylinders']:
        
        cyl = cylinder.Cylinder(data['id'], data['diameter'], data['weight'])

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
            max_attempts = 100
            
            for num_attempts in range(max_attempts):
                rand_x = random.uniform(cyl.radius, cont_w - cyl.radius)
                rand_y = random.uniform(cyl.radius, cont_h - cyl.radius)
                
                cyl.set_position(rand_x, rand_y)

                
                collision = False
                for other_cyl in placed_cylinders:
                    if cyl.overlaps(other_cyl):
                        collision = True
                        break 
                
                is_accessible = False
                if not collision:
                    is_accessible = order.check_access(cyl, placed_cylinders) ## Check placement with relation to rear loading constraint
                    
                    if is_accessible: ## comment this line and un-indent following code to test without rear loading constraint
                        placed_cylinders.append(cyl)
                        total_weight += cyl.weight
                        placed = True
                        # print(f"Placed Cylinder {cyl.id} after {num_attempts} attempts")
                        total_attempts += num_attempts
                        break 
            
            if not placed:
                print(f"Could not place Cylinder {cyl.id} after {max_attempts} attempts.") 
    print(f"Total number of attempts failed: {total_attempts}")
    fitness_score, com_X, com_Y = fitness.check_fitness(current_inst, placed_cylinders, verbose=True)
    vis.visualise_container(current_inst, com_x = com_X, com_y = com_Y, placed_cylinders=placed_cylinders)

