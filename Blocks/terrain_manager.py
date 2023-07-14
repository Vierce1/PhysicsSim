from Blocks.block import Block
import Blocks.block_type as block_type
import pygame as pg
import math
import sys
import random



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
        self.destroyable_blocks = set()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        self.first_trigger_radius = 10
        self.gravity = 1
        self.terminal_velocity = 1
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.matrix = {}
        for x in range(-10, screen_width + 10):  # initalize all spaces as empty
            for y in range(-10, screen_height + 10):
                self.matrix[x,y] = (0, None)
        # print(f'matrix length: {len(self.matrix)}')



    def setup(self, render_image):  # need new method for adding blocks after init
        for b in self.blocks:
            self.matrix[b.position[0], b.position[1]] = (OCCUPIED, b)
        self.render_image = render_image


    # @profile
    def update(self, screen) -> None:
        for block in self.blocks:
            self.update_blocks(block=block, screen=self.render_image)

        self.inactive_blocks.update({b for b in self.blocks if not b.collision_detection})
        self.blocks = {b for b in self.blocks if b.collision_detection}
        # print(len([b for b in self.blocks]))
        # print(len(self.blocks))





# Physics

    # TODO: Need to ravamp this for speed changes
    def check_under(self, position: (int, int)) -> bool:
        if position[1] == ground:
            return True
        return self.matrix[position[0], position[1] + 1][0] == 1


    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        # if self.screen_width > block.position[0] + dir > 0 \  # costs fps
        #   and self.screen_height > block.position[1] + dir > 0:
        if self.matrix[block.position[0] + dir, block.position[1] + 1][0] == EMPTY:
            return dir
        elif self.matrix[block.position[0] - dir, block.position[1] + 1][0] == EMPTY:
            return -dir
        return 0

    def check_slope(self, position: (int, int), direction: int) -> bool:
        if self.matrix[position[0] + direction[0], position[1] - 1][0] == EMPTY:
            return True
        return False





    # Block functions
    def update_blocks(self, block, screen):
        if block.collision_detection:
            if block.grounded_timer >= frames_til_grounded:
                block.collision_detection = False
                self.inactive_blocks.add(block)
            self.move(block)
        screen.set_at(block.position, block.type.color)


    # @profile
    def move(self, block):
        if block.position[1] == ground - 1:
            block.horiz_velocity = 0
            return

        collision = self.check_under(block.position)

        if collision:  # collided. Check if it should slide to either side + down 1
            block.vert_velocity = 0
            block.grounded_timer += 1  # Increment grounded timer to take inactive blocks out of set

            slide = self.check_slide(block)
            if slide != 0:
                self.slide(block, slide)
            return

        if block.vert_velocity < self.terminal_velocity:
            block.vert_velocity += self.gravity

        # mark prev position empty & mark to fill with black
        self.matrix[block.position[0], block.position[1]] = (EMPTY, None)
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0], block.position[1] + block.vert_velocity)
#TODO: If want to incorporate block width/height, need to draw all pixels contained here
#That adds complexity to 1-width blocks, though
        self.matrix[block.position[0], block.position[1]] = (OCCUPIED, block)
        return


    def slide(self, block: Block, slide: int) -> None:
        block.horiz_velocity = slide * 1 * slide_factor
        self.matrix[block.position[0], block.position[1]] = (EMPTY, None)
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0] + block.horiz_velocity, block.position[1])
        self.matrix[block.position[0], block.position[1]] = (OCCUPIED, block)
        return


    def destroy_block(self, block: Block) -> None:
        self.matrix[block.position[0], block.position[1]] = (EMPTY, None)
        self.game.spaces_to_clear.add(block.position)


    def trigger_ungrounding(self, position: (int, int), call_count: int = 0):
        call_count += 1
        triggered = False
        radius = self.first_trigger_radius * call_count
        for y in range(position[1]-radius, position[1]+radius):
            for x in range(position[0]-radius, position[0]+radius):
                if y < 0 or x < 0 or y > self.screen_height or x > self.screen_width:
                    continue
                # print(f'checking {x}  {y}')
                check_pos = (x, y)
                block = self.matrix[check_pos[0], check_pos[1]][1]
                if not block or block.type.rigid or block not in self.inactive_blocks:
                    continue
                block.collision_detection = True
                block.grounded_timer = 0
                self.blocks.add(block)
                self.inactive_blocks.remove(block)
                triggered = True

        if triggered:
            self.trigger_ungrounding(position=position, call_count=call_count)



