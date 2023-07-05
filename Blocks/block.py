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
        self.rect = pg.Rect(position[0], position[1], 6,6)
        self.quadtree = None
        self.collision_detection = not type.rigid  # False for rigid=True blocks
        self.grounded_timer = 0
        self.neighboring_blocks = []
        self.bottom_collide_block = None


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
        # self.neighboring_blocks = self.quadtree.get_neighbors()
        self.bottom_collide_block = None
        self.neighboring_blocks = self.t_m.get_update_neighbors(self.quadtree)
        collision = physics.check_down_collision(self, self.neighboring_blocks)

        if collision:  # collided. Check if it should slide to either side
            self.vert_velocity = 0
            if collision != True:  # true means ground
                self.bottom_collide_block = collision
#TODO: is this causing slowdowns?
            if type(collision) is Block and collision.vert_velocity == 0:
                slide = physics.check_slide(self, collision)
                # check if there is a block in the way to stop sliding that direction
                self.horiz_velocity = slide * self.rect.width * physics.slide_factor
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
        if self.vert_velocity > 0 or self.grounded_timer > physics.frames_til_grounded \
                or (self.bottom_collide_block and self.bottom_collide_block.vert_velocity > 0):
            return self.position
        if physics.check_side_collision(self, self.neighboring_blocks, self.horiz_velocity < 0):
            self.horiz_velocity = 0
            return self.position
        # not blocked to the side trying to slide
        position = (self.position[0] + self.horiz_velocity, self.position[1])
        self.rect.left = position[0]
        self.rect.top = position[1]
        return position