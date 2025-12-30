## cylinder.py
import random
import numpy as np

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