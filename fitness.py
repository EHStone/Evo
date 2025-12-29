import custom_visualiser as vis

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

def check_fitness(instance, solution):
    if not solution:
        print("No cylinders placed.")
        return 0, 0
    # print(solution)

    ## Calculate center of mass and punish if out of boundaries (invalid solution)

    # Container Boundaries
    min_com_x, min_com_y, box_w, box_h = vis.visualise_container(instance, show_vis=False)
    max_com_x = min_com_x + box_w
    max_com_y = min_com_y + box_h
    com_X, com_Y, solution_weight = calc_com(solution)
    if com_X > max_com_x or com_X < min_com_x or com_Y > max_com_y or com_Y < min_com_y:
        fitness = 100 ## arbitrary large positive number to represent poor fitness score
        print("Failure, COM ", instance['name'])
        return fitness, com_X, com_Y
    
    ## TODO Calculate total weight and punish if overweight (invalid)
     # note that current baseline already denies overweight solution, this is purely for future use
    if check_overweight(instance, solution_weight):
        fitness = 100  ## arbitrary large positive number to represent poor fitness score
        return fitness    
    ## TODO create a fitness function


    fitness = 0 
    print("Success", instance['name'])
    return fitness, com_X, com_Y