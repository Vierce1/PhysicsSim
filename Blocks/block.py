import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type
# import sys

class Reduce(type):
    def __new__(cls, name, bases, attrs):
        attrs['__dict__'] = {}
        return super().__new__(cls, name, bases, attrs)


class Block: # no change in size. (metaclass=Reduce):
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        # print(sys.getsizeof(self ))
        # self.id = -1
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
