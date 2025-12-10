import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

class Circle:
    def __init__(self, radius, circle_id):
        self.x = 0
        self.y = 0
        self.radius = radius
        self.id = circle_id
        self.computed = False  # Has position been determined?
    
    def compute_position(self, other_circles, center_x, center_y):
        """Calculate shells, find open points, choose best"""
        open_points = []
        
        # For each existing circle, calculate shell points
        for other in other_circles:
            if other.computed:
                shell_radius = self.radius + other.radius
                
                # Sample points around the shell
                for angle in range(0, 360, 1):  # Every 1 degree
                    angle_rad = math.radians(angle)
                    px = other.x + math.cos(angle_rad) * shell_radius
                    py = other.y + math.sin(angle_rad) * shell_radius
                    
                    # Check if this point causes overlaps
                    valid = True
                    for check in other_circles:
                        if check.computed:
                            if self._would_overlap(px, py, check):
                                valid = False
                                break
                    
                    if valid:
                        open_points.append((px, py))
        
        # Choose point closest to center
        if open_points:
            best_point = min(open_points, 
                           key=lambda p: math.dist((p[0], p[1]), 
                                                  (center_x, center_y)))
            self.x, self.y = best_point
        
        self.computed = True
        return open_points
    
    def _would_overlap(self, px, py, other):
        """Check if placing at (px, py) would overlap with other"""
        dx = px - other.x
        dy = py - other.y
        distance_squared = dx*dx + dy*dy
        radius_sum = self.radius + other.radius
        return distance_squared < (radius_sum * radius_sum)

class Bunch:
    def __init__(self, radii):
        """Create circles with given radii in given order"""
        self.circles = [Circle(r, i) for i, r in enumerate(radii)]
        self.center_x = 400  # Assuming 800x600 canvas
        self.center_y = 300
        self.open_points = []
    
    def ordered_place(self):
        """Place circles sequentially"""
        # Place first circle at center
        self.circles[0].x = self.center_x
        self.circles[0].y = self.center_y
        self.circles[0].computed = True
        
        # Place remaining circles
        for i in range(1, len(self.circles)):
            self.open_points = self.circles[i].compute_position(
                self.circles, self.center_x, self.center_y
            )
    
    def compute_boundary(self):
        """Calculate bounding circle radius (fitness)"""
        max_distance = 0
        
        for circle in self.circles:
            if circle.computed:
                dx = circle.x - self.center_x
                dy = circle.y - self.center_y
                dist_to_center = math.sqrt(dx*dx + dy*dy)
                dist_to_edge = dist_to_center + circle.radius
                
                if dist_to_edge > max_distance:
                    max_distance = dist_to_edge
        
        return max_distance

def visualize_packing(bunch):
    """Visualize the circle packing"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    
    # Draw bounding circle
    boundary = bunch.compute_boundary()
    bounding_circle = patches.Circle(
        (bunch.center_x, bunch.center_y), boundary,
        fill=False, edgecolor='#F4BA02', linewidth=2
    )
    ax.add_patch(bounding_circle)
    
    # Draw each circle
    for circle in bunch.circles:
        if circle.computed:
            c = patches.Circle(
                (circle.x, circle.y), circle.radius,
                fill=True, facecolor='#99D9DD', 
                edgecolor='#01364C', alpha=0.7
            )
            ax.add_patch(c)
            
            # Add label
            ax.text(circle.x, circle.y, str(circle.id),
                   ha='center', va='center', fontsize=10)
    
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.set_title(f'Bounding Radius: {boundary:.2f}')
    plt.show()

# Example usage
radii = [40, 25, 35, 20, 15, 18]
bunch = Bunch(radii)
bunch.ordered_place()
visualize_packing(bunch)