from Blocks.block import Block
import Blocks.block_type as block_type
import pygame as pg
import math
import sys
import random


gravity = 1
terminal_velocity = 1
display_res = []
ground = 705
frames_til_grounded = 120  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally
EMPTY = 0
OCCUPIED = 1


class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int, game):
        self.blocks = set()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.matrix = {}
        for x in range(screen_width):  # initalize all spaces as empty
            for y in range(screen_height):
                self.matrix[x,y] = 0
        print(f'matrix length: {len(self.matrix)}')



    def setup(self, render_image):  # need new method for adding blocks after init
        for b in self.blocks:
            self.matrix[b.position[0], b.position[1]] = OCCUPIED
        self.render_image = render_image


    # @profile
    def update(self, screen) -> list:
        # [self.game.spaces_to_clear.add(pos) for pos in self.matrix if pos == EMPTY]

        for block in self.blocks:
            self.update_blocks(block=block, screen=self.render_image)




# Physics

    def check_under(self, block: Block):
        if block.position[1] == ground:
            return True
        return self.matrix[block.position[0], block.position[1] + block.height] == 1


    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        if self.matrix[block.position[0] + block.width * dir, block.position[1] + block.height] == 0:
            return 1
        elif self.matrix[block.position[0] + block.width * -dir, block.position[1] + block.height] == 0:
            return -1
        return 0





    # Block functions
    def update_blocks(self, block, screen):
        if block.collision_detection:
            if block.grounded_timer == frames_til_grounded:
                block.collision_detection = False
            self.move(block)
        screen.set_at(block.position, block.type.color)


    # @profile
    def move(self, block):
        if block.position[1] == ground - 1:
            block.horiz_velocity = 0
            return

        collision = self.check_under(block)

        if collision:  # collided. Check if it should slide to either side + down 1
            block.vert_velocity = 0

            slide = self.check_slide(block)
            if slide != 0:
                self.slide(block, slide)
            return

        if block.vert_velocity < terminal_velocity:
            block.vert_velocity += gravity

        # mark prev position empty & mark to fill with black
        self.matrix[block.position[0], block.position[1]] = 0
        # self.game.spaces_to_clear.add((block.position[0], block.position[1]))  # Slower with more particles updating
        block.position = (block.position[0], block.position[1] + block.vert_velocity)
        self.matrix[block.position[0], block.position[1]] = 1
        return


    def slide(self, block: Block, slide: int) -> None:
        block.horiz_velocity = slide * 1 * slide_factor
        self.matrix[block.position[0], block.position[1]] = EMPTY
        # self.game.spaces_to_clear.add((block.position[0], block.position[1]))  # Slower with more particles updating
        block.position = (block.position[0] + block.horiz_velocity, block.position[1])
        self.matrix[block.position[0], block.position[1]] = OCCUPIED
        return


