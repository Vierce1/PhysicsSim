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
frames_til_grounded = 320  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally - currently unused
EMPTY = 0
OCCUPIED = 1


class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int, game):
        self.blocks = set()
        self.inactive_blocks = set()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.matrix = {}
        for x in range(screen_width):  # initalize all spaces as empty
            for y in range(screen_height):
                self.matrix[x,y] = 0
        # print(f'matrix length: {len(self.matrix)}')



    def setup(self, render_image):  # need new method for adding blocks after init
        for b in self.blocks:
            self.matrix[b.position[0], b.position[1]] = OCCUPIED
        self.render_image = render_image


    # @profile
    def update(self, screen) -> None:
        for block in self.blocks:
            self.update_blocks(block=block, screen=self.render_image)

        self.inactive_blocks.update({b for b in self.blocks if not b.collision_detection})
        self.blocks = {b for b in self.blocks if b.collision_detection}

        # print(len(self.blocks))





# Physics

    def check_under(self, block: Block):
        if block.position[1] == ground:
            return True
        return self.matrix[block.position[0], block.position[1] + 1] == 1


    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        if self.matrix[block.position[0] + dir, block.position[1] + 1] == EMPTY:
            return dir
        elif self.matrix[block.position[0] - dir, block.position[1] + 1] == EMPTY:
            return -dir
        return 0





    # Block functions
    def update_blocks(self, block, screen):
        if block.collision_detection:
            if block.grounded_timer >= frames_til_grounded:
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
            block.grounded_timer += 1  # Increment grounded timer to take inactive blocks out of set

            slide = self.check_slide(block)
            if slide != 0:
                self.slide(block, slide)
            return

        if block.vert_velocity < terminal_velocity:
            block.vert_velocity += gravity

        # mark prev position empty & mark to fill with black
        self.matrix[block.position[0], block.position[1]] = EMPTY
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0], block.position[1] + block.vert_velocity)
#TODO: If want to incorporate block width/height, need to draw all pixels contained here
#That adds complexity to 1-width blocks, though
        self.matrix[block.position[0], block.position[1]] = OCCUPIED
        return


    def slide(self, block: Block, slide: int) -> None:
        block.horiz_velocity = slide * 1 * slide_factor
        self.matrix[block.position[0], block.position[1]] = EMPTY
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0] + block.horiz_velocity, block.position[1])
        self.matrix[block.position[0], block.position[1]] = OCCUPIED
        return


    def destroy_block(self, block: Block) -> None:
        self.matrix[block.position[0], block.position[1]] = EMPTY
        self.game.spaces_to_clear.add(block.position)


