import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type
# import sys


class Block:
    # slots reduces size of object by only reserving enough memory to hold these values.
    __slots__ = ('id', 'type', 'position', 'width', 'height', 'vert_velocity', 'horiz_velocity', 'collision_detection',
                 'grounded_timer')
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        # print(sys.getsizeof(self ))
        self.id = 0
        self.type = type
        self.position = position
        self.width = type.width
        self.height = type.height
        # self.move_speed = 1 #.03  # different blocks can fall different speeds
        self.vert_velocity = 0
        self.horiz_velocity = 0
        # self.rect = pg.Rect(position[0], position[1], 1, 1) # removed, draw specific pixels
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.grounded_timer = 0
