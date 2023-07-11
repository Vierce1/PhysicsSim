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
        self.move_speed = .03  # different blocks can fall different speeds
        self.vert_velocity = 0
        self.horiz_velocity = 0
        self.rect = pg.Rect(position[0], position[1], 3,3)
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.grounded_timer = 0
        self.bottom_collide_block = None
        self.leaves = []
        self.z_address = 0x00


