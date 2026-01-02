# ordered_packing.py
import numpy as np

def check_access(new_cylinder, placed_cylinders):

    for obstacle in placed_cylinders:
        ## Check for horizontal overlap
        delta_x = abs(new_cylinder.x - obstacle.x)
        min_clearance = new_cylinder.radius + obstacle.radius + 0.05

        if delta_x < min_clearance:
            
            # check bertical position (Blocking from Top)
            # If the obstacle is "above" the new cylinder 
            if obstacle.y > new_cylinder.y:
                return False ## Rear loading constraint failed
                
    return True ## Rear loading constraint passed