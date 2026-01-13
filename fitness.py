import custom_visualiser as vis
import math
import ordered_packing as order

 #### TODO consider missing cylinders (i.e. punish if not all cylinders included)
def calc_com(solution):
    total_weight = 0
    sum_moment_x = 0
    sum_moment_y = 0

    for cyl in solution:
        
        total_weight += cyl.weight
        sum_moment_x += (cyl.weight * cyl.x)
        sum_moment_y += (cyl.weight * cyl.y)

    com_x = sum_moment_x / total_weight
    com_y = sum_moment_y / total_weight
    return com_x, com_y, total_weight


def check_overweight(instance, solution_weight):
    max_weight = instance['container']['max_weight']
    if solution_weight > max_weight:
        return True ## Overweight (invalid)
    return False ## underweight (valid)

def check_com(instance, solution):
    ## Calculate center of mass and punish if out of boundaries (invalid solution)

    # Container Boundaries
    min_com_x, min_com_y, com_box_w, com_box_h = vis.visualise_container(instance, show_vis=False)
    max_com_x = min_com_x + com_box_w
    max_com_y = min_com_y + com_box_h
    com_X, com_Y, solution_weight = calc_com(solution)
    if com_X > max_com_x or com_X < min_com_x or com_Y > max_com_y or com_Y < min_com_y:
        return solution_weight, True, com_X, com_Y
    return solution_weight, False, com_X, com_Y

def check_num_unplaced(instance, solution):
    total_cylinders = instance['cylinders']
    if len(total_cylinders) > len(solution):
        return len(total_cylinders) - len(solution)
    return 0

def check_overlaps(solution):
    num_overlaps = 0
    for cyl in solution:
        for other_cyl in solution:
            if other_cyl != cyl and cyl.overlaps(other_cyl):
                num_overlaps += 1
    return num_overlaps

def check_rear_loading(solution):
    num_inaccessible = 0
    previous_cylinders = []
    for cyl in solution:
        if previous_cylinders:
            is_accessible = order.check_access(cyl, previous_cylinders) ## Check placement with relation to rear loading constraint
            if not is_accessible:
                num_inaccessible += 1
        previous_cylinders.append(cyl)
    return num_inaccessible
                

def check_fitness(instance, solution, verbose = False):
    fitness = 0
    valid = ""
    if not solution:
        print("No cylinders placed.")
        return 1000, 0, 0

    solution_weight, com_result, com_X, com_Y = check_com(instance, solution)
    
    if com_result: ##COM Failed
        fitness += 100 ## arbitrary large positive number to represent poor fitness score
        valid = valid + "COM Failure, "
        
    

     # note that current baseline already denies overweight solution, this is purely for future use
    if check_overweight(instance, solution_weight):
        fitness += 100  ## arbitrary large positive number to represent poor fitness score
        valid = valid + "Overweight Failure, "
          
    unplaced_cylinders = check_num_unplaced(instance, solution)
    fitness += (10 * unplaced_cylinders)
    if (unplaced_cylinders > 0): valid = valid + "Did not place all cylinders, "

    num_overlaps = check_overlaps(solution)
    fitness += (num_overlaps * 50)
    if (num_overlaps > 0): valid = valid + "Overlaps present, "

    num_inaccessible = check_rear_loading(solution)
    fitness += (num_inaccessible * 50)
    if (num_inaccessible > 0): valid = valid + "Rear loading violation, "
    ## fitness calculation based on combiunation of packing density & COM centralisation

    ## Get container dimensions again for calculation
    min_com_x, min_com_y, com_box_w, com_box_h = vis.visualise_container(instance, show_vis=False)
    

    ## ------------------ Packing Density ------------- ##

    # # Calculate the extent of the solution (Bounding Box)
    # # We use list comprehensions to find the min/max extents including the radius
    # sol_min_x = min([c.x - c.radius for c in solution])
    # sol_max_x = max([c.x + c.radius for c in solution])
    # sol_min_y = min([c.y - c.radius for c in solution])
    # sol_max_y = max([c.y + c.radius for c in solution])

    # # Calculate Areas
    # bbox_width = sol_max_x - sol_min_x
    # bbox_height = sol_max_y - sol_min_y
    
    # # Protect against zero-area (single point) issues, though unlikely with radii > 0
    # bbox_area = bbox_width * bbox_height
    # if bbox_area <= 0:
    #     bbox_area = 1e-9 

    # # Sum of areas of actual cylinders (Area = pi * r^2)
    # total_cyl_area = sum([math.pi * (c.radius ** 2) for c in solution])

    # # Density Ratio: How much of the bounding box is filled? (0.0 to ~0.90)
    # density_ratio = total_cyl_area / bbox_area

    # # Density Cost: Invert so that Higher Density = Lower Cost
    # # If cylinders are far apart, bbox_area is huge, ratio is small, cost is ~1.0
    # # If cylinders are touching, bbox_area is small, ratio is high, cost is ~0.2
    # density_cost = 1.0 - density_ratio

    ## ------------------ COM Centralisation ------------- ##

    ## Find center of the container
    center_x = min_com_x + (com_box_w / 2)
    center_y = min_com_y + (com_box_h / 2)
    
    distance = math.dist((com_X, com_Y), (center_x, center_y))
    
    ## Normalise distance: 0.0 (at center) to 1.0 (at edge of box)
    max_possible_dist = math.sqrt((com_box_w/2)**2 + (com_box_h/2)**2)
    balance_cost = distance / max_possible_dist

    ## ---------------- final fitness calc -------------- ##

    # Adjust weights to prioritise packing density vs COM balancing 
    w_pack = 1
    w_bal = 1
    
    # fitness += (w_pack * density_cost) + (w_bal * balance_cost)

    fitness +=  (w_bal * balance_cost)
    if valid == "":
        valid = "Success, "
    if verbose:
        # print(density_cost, ' ', balance_cost)
        print(f"{valid}Fitness: {round(fitness, 2)}")
    return fitness, com_X, com_Y