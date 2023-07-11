import pygame as pg
import Blocks.block_type as block_type
import Blocks.block_type


class Block:
    def __init__(self, type: block_type.Block_Type, position: (int, int)):
        self.id = -1
        self.type = type
        self.position = position
        self.move_speed = .03  # different blocks can fall different speeds
        self.vert_velocity = 0
        self.horiz_velocity = 0
        # self.t_m = terrain_manager
        self.rect = pg.Rect(position[0], position[1], 3,3)
        # self.quadtree = None
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.grounded_timer = 0
        # self.neighboring_blocks = []
        self.bottom_collide_block = None
        self.leaves = []
        self.z_address = 0x00
