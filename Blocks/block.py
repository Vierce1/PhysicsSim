import pygame as pg
import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
# from Blocks import terrain_manager as tm
import Blocks.terrain_manager as tm
import physics


class Block:
    def __init__(self, type: block_type.Block_Type, position: (int, int) , terrain_manager: tm.Terrain_Manager):
        self.type = type
        self.position = position
        self.move_speed = .03  # different blocks can fall different speeds
        self.vert_velocity = 0
        self.t_m = terrain_manager
        self.rect = pg.Rect(position[0], position[1], 10, 10)
        self.quadtree = None
        self.collision_detection = True  # starts off then when triggered begins detection
        self.grounded_timer = 0


    def update(self, screen):
        if self.grounded_timer == 20:
            self.collision_detection = False
        self.position = self.move()
        pg.draw.rect(surface=screen, color=(150,190,0), rect=self.rect)

    def move(self):
        if not self.collision_detection or not self.quadtree:
            return
        neighboring_blocks = self.quadtree.get_neighbors()
        collisions = physics.check_collision(self, neighboring_blocks)
        if collisions:
            self.vert_velocity = 0
            return self.position
        if self.vert_velocity < physics.terminal_velocity:
            self.vert_velocity += (physics.gravity * self.move_speed)
        position = (self.position[0], self.position[1] + self.vert_velocity)
        self.rect.left = position[0]
        self.rect.top = position[1]
        return position
