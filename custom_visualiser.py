import container_instances as inst
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualise_container(instance, show_vis = True, com_x = 0, com_y = 0, placed_cylinders = None):
    container = instance['container']
    # print("Generating visualisation for container: ", container)
    ## Fetch width and height from instance's container dict
    container_w = container['width']
    container_h = container['depth']
    
    ## Calculate dimensions for second box representing center 60%
    box_w = container_w * 0.60
    box_h = container_h * 0.60
    

    box_x = (container_w - box_w) / 2
    box_y = (container_h - box_h) / 2
    
    if show_vis:
        fig, ax = plt.subplots(figsize=(6, 6))
        ## Container (Outer Box)
        container_vis = patches.Rectangle(
            (0, 0), container_w, container_h, 
            linewidth=2, edgecolor='black', facecolor='none', label='Container'
        )
        
        ## Inner Box
        center_box = patches.Rectangle(
            (box_x, box_y), box_w, box_h, 
            linewidth=2, edgecolor='red', facecolor='red', alpha=0.3, label='Center 60%'
        )
        
        ax.add_patch(container_vis)
        ax.add_patch(center_box)
        
        if placed_cylinders:
            id_with_order = []
            iter = 1
            for cyl in placed_cylinders:
                circle = patches.Circle(
                    (cyl.x, cyl.y), 
                    radius=cyl.radius, 
                    edgecolor='black', 
                    facecolor=getattr(cyl, 'color', 'blue'), # Default to blue if no color
                    alpha=0.6
                )
                ax.add_patch(circle)
                if hasattr(cyl, 'id'):
                    ax.text(cyl.x, cyl.y, f"ID: {str(cyl.id)}", ha='center', va='center', 
                            color='white', fontsize=8, fontweight='bold')
                    id_with_order.append([cyl.id, iter])
                    iter += 1
            com = patches.Circle(
                    (com_x, com_y), 
                    radius=.1, 
                    edgecolor='black', 
                    facecolor='red',
                    label='COM'
                )
            ax.add_patch(com)


        ## Set limits slightly larger than container to see borders clearly
        ax.set_xlim(-container_w * 0.1, container_w * 1.1)
        ax.set_ylim(-container_h * 0.1, container_h * 1.1)

        ax.set_aspect('equal') 
        ax.legend(loc='upper right')
        ax.set_title(f"Container: {container_w}x{container_h} | Max Weight: {container['max_weight']}")
        ax.axis('off')

        table_data = [[item[0], item[1]] for item in id_with_order]
        table_data.sort(key=lambda x: x[0])
        if table_data:
            # 2. Add a table to the right of the plot
            # loc='right' centers it vertically on the right side
            the_table = ax.table(
                cellText=table_data,
                colLabels=['ID', 'Order'],
                loc='right',
                cellLoc='center',
                colWidths=[0.15, 0.15] # Adjust width as needed
            )
            
            # Scale the table slightly so text is readable
            the_table.scale(1, 1.5)
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(9)

            # 3. Adjust the main plot layout to make room for the table
            # 'right=0.7' means the plot takes up 70% of the width, leaving 30% for the table
            plt.subplots_adjust(left=0.05, right=0.75)
        plt.show()

    return box_x, box_y, box_w, box_h

# ## Fetch instances from provided file and test visualiser
# all_instances = inst.generate_all_instances()
# basic_instances = all_instances['basic_instances']
# visualise_container(basic_instances[0])
