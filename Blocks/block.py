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
        self.horiz_velocity = 0
        self.t_m = terrain_manager
        self.rect = pg.Rect(position[0], position[1], 5, 5)
        self.quadtree = None
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.grounded_timer = 0


    def update(self, screen):
        if self.grounded_timer == physics.frames_til_grounded:
            self.collision_detection = False
        self.position = self.move()
        self.position = self.slide()
        pg.draw.rect(surface=screen, color=self.type.color, rect=self.rect)

    def move(self):
        if not self.collision_detection or not self.quadtree:
            self.horiz_velocity = 0
            return self.position
        neighboring_blocks = self.quadtree.get_neighbors()
        collision = physics.check_collision(self, neighboring_blocks)
        if collision:  # collided. Check if it should slide to either side
            self.vert_velocity = 0
#TODO: is this causing slowdowns?
            if type(collision) is Block:
            # if isinstance(collision, Block):
                slide = physics.check_slide(self, collision)
                self.horiz_velocity += slide * self.rect.width / 20
                # position = (self.position[0] + self.horiz_velocity, self.position[1])
            return self.position
        if self.vert_velocity < physics.terminal_velocity:
            self.vert_velocity += (physics.gravity * self.move_speed)
        position = (self.position[0], self.position[1] + self.vert_velocity)
        # self.rect = self.rect.move(position[0] - self.rect.x, position[1] - self.rect.y)
#TODO: Which is more efficient?
        self.rect.left = position[0]
        self.rect.top = position[1]
        return position

    def slide(self):
        if self.vert_velocity != 0 or self.grounded_timer > physics.frames_til_grounded:
            return self.position
        position = (self.position[0] + self.horiz_velocity, self.position[1])
        self.rect.left = position[0]
        self.rect.top = position[1]
        return position