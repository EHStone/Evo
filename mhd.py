import math
import custom_visualiser as vis
# import container_instances as inst
import ordered_packing as order
import fitness
import cylinder
import numpy as np
import random

def get_tangent_positions(c1, c2, new_r):
    """
    Calculates the two positions where a new circle of radius new_r
    is tangent to both circle c1 and circle c2.
    """
    r1 = c1.radius + new_r
    r2 = c2.radius + new_r
    
    # Calculate distance between centers of c1 and c2
    dx = c2.x - c1.x
    dy = c2.y - c1.y
    d = math.sqrt(dx*dx + dy*dy)
    
    # Check for validity (triangle inequality)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []

    # 'a' is the distance from c1 to the intersection of the radical axis
    a = (r1**2 - r2**2 + d**2) / (2*d)
    
    # 'h' is the distance from the radical axis to the intersection points
    h_arg = r1**2 - a**2
    h = math.sqrt(max(0, h_arg))
    
    # Point P2 is the intersection of the line connecting centers and the radical axis
    p2_x = c1.x + a * (dx / d)
    p2_y = c1.y + a * (dy / d)
    
    # Calculate the two intersection points
    x3_1 = p2_x + h * (dy / d)
    y3_1 = p2_y - h * (dx / d)
    
    x3_2 = p2_x - h * (dy / d)
    y3_2 = p2_y + h * (dx / d)
    
    return [(x3_1, y3_1), (x3_2, y3_2)]

def find_candidate_positions(placed_cylinders, new_cyl, cont_w, cont_h, center_point):
    """
    Generates a list of valid 'nooks' (tangent points) where the new cylinder 
    can nest against existing ones.
    """
    candidates = []
    
    # If only 1 cylinder is placed, place strictly around it
    if len(placed_cylinders) == 1:
        c1 = placed_cylinders[0]
        dist = c1.radius + new_cyl.radius + 0.1
        # Try 36 positions around the first cylinder
        for angle in np.linspace(0, 2*np.pi, 36, endpoint=False):
            x = c1.x + dist * np.cos(angle)
            y = c1.y + dist * np.sin(angle)
            candidates.append((x, y))
            
    else:
        # Iterate through all pairs of placed cylinders to find "nooks"
        for i in range(len(placed_cylinders)):
            for j in range(i + 1, len(placed_cylinders)):
                c1 = placed_cylinders[i]
                c2 = placed_cylinders[j]
                
                points = get_tangent_positions(c1, c2, new_cyl.radius)
                candidates.extend(points)

    # Filter and Validate Candidates
    valid_positions = []
    
    for (x, y) in candidates:
        # 1. Check Container Boundaries (stay inside walls)
        if (x - new_cyl.radius < 0 or x + new_cyl.radius > cont_w or 
            y - new_cyl.radius < 0 or y + new_cyl.radius > cont_h):
            continue

        # Update temp position for collision check
        new_cyl.set_position(x, y)

        # 2. Check Overlap with ALL other placed cylinders
        collision = False
        for other in placed_cylinders:
            if new_cyl.overlaps(other):
                collision = True
                break
        
        if not collision:
            # Calculate distance to center (for sorting preference)
            dist_to_center = math.sqrt((x - center_point[0])**2 + (y - center_point[1])**2)
            valid_positions.append({'x': x, 'y': y, 'dist': dist_to_center})

    # Sort valid positions: Prefer those closest to the center of the container
    # This mimics the Bunch "containing radius" minimization
    valid_positions.sort(key=lambda p: p['dist'])
    
    return valid_positions


# --- Main Algorithm ---

def run_mhd(current_inst):

    box_x, box_y, box_w, box_h = vis.visualise_container(current_inst, show_vis=False)
    center_point = (box_x + box_w/2, box_y + box_h/2)

    placed_cylinders = [] 
    total_weight = 0
    check_first_placed = 1 

    # Container Boundaries
    cont_w = current_inst['container']['width']
    cont_h = current_inst['container']['depth']
    
    # print(f"--- Processing Container ({cont_w}x{cont_h}) ---")

    for data in current_inst['cylinders']:
        
        cyl = cylinder.Cylinder(data['id'], data['diameter'], data['weight'])

        ## check if adding will result in overweight
        if (total_weight + cyl.weight) > current_inst['container']['max_weight']:
            # print(f"Skipping Cylinder {cyl.id}: Max weight exceeded.")
            continue
        
        placed = False
        
        ## 1. Place First Cylinder in Center
        if check_first_placed == 1:
            cyl.set_position(center_point[0], center_point[1])
            placed_cylinders.append(cyl)
            total_weight += cyl.weight
            check_first_placed = 0
            placed = True
            # print(f"Placed Cylinder {cyl.id} (First) at Center")
            
        else:
            # Get all valid open spots relative to existing cylinders
            candidates = find_candidate_positions(placed_cylinders, cyl, cont_w, cont_h, center_point)
            for pos in candidates:
                cyl.set_position(pos['x'], pos['y'])
                
                ## Check Accessibility (Rear loading)
                ## Note that with this, cylinder placement trends upwards
                 ## without, cylinders are placed in a well packed area
                is_accessible = order.check_access(cyl, placed_cylinders)
                
                if is_accessible:
                    placed_cylinders.append(cyl)
                    total_weight += cyl.weight
                    placed = True
                    break 
            
            if not placed:
                print(f"Could not place Cylinder {cyl.id} (No valid geometric slot found).") 

    fitness_score, com_X, com_Y = fitness.check_fitness(current_inst, placed_cylinders, verbose=True)
    vis.visualise_container(current_inst, com_x=com_X, com_y=com_Y, placed_cylinders=placed_cylinders)