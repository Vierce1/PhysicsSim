import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type
# import sys
# from numba.experimental import *

# @jitclass
class Block:
    # slots reduces size of object by only reserving enough memory to hold these values.
    __slots__ = ('id', 'type', 'position', 'vert_velocity', 'horiz_velocity',
                 'collision_detection')
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        # print(sys.getsizeof(self ))
        self.id = 0
        self.type = type
        self.position = position
        self.vert_velocity = 0
        self.horiz_velocity = 0
        self.collision_detection = not type.rigid  # False for rigid=True blocks


class Ghost_Particle:
    __slots__ = ('position', 'parent_id', 'color')
    def __init__(self, position: (int, int), parent_id: int, color: (int, int, int)):
        self.position = position
        self.parent_id = parent_id
        self.color = color
        # Do I need an id?

    def update(self):
        pass