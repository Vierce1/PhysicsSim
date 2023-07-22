import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type
# import sys


class Block:
    # slots reduces size of object by only reserving enough memory to hold these values.
    __slots__ = ('id', 'type', 'color_index', 'position', 'vert_velocity', 'horiz_velocity',
                 'collision_detection')
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        # print(sys.getsizeof(self ))
        self.id = 0
        self.type = type
        self.position = position
        self.vert_velocity = 0
        self.horiz_velocity = 0
        self.collision_detection = not type.rigid  # False for rigid=True blocks
