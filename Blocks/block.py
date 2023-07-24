import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type
# import sys
# from numba.experimental import *
import math


# @jitclass
class Block:
    # slots reduces size of object by only reserving enough memory to hold these values.
    __slots__ = ('id', 'type', 'position', 'vert_velocity', 'horiz_velocity',
                 'collision_detection', 'trail_created')
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        # print(sys.getsizeof(self ))
        self.id = 0
        self.type = type
        self.position = position
        self.vert_velocity = 0
        self.horiz_velocity = 0
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.trail_created = False


class Trail:
    __slots__ = ('position', 'parent_id', 'color')
    def __init__(self, parent_id: int, color: (int, int, int)):
        self.position = (0, 0)
        self.parent_id = parent_id  # is holding the actual object in memory more efficient, or passing it in each frame
        self.color = color
        # Do I need an id?

    def update_pos(self, parent: Block):
        if parent.vert_velocity == 0 and parent.horiz_velocity == 0:
            parent.trail_created = False
            return None
        new_pos = (int(parent.position[0] - math.ceil(parent.horiz_velocity / 5))
                    , int(parent.position[1] - math.ceil(parent.vert_velocity / 5)))
        self.position = new_pos
        return new_pos
