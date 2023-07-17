from Blocks.block import Block
import Blocks.block_type as block_type
from quadtree import Quadtree_Node, Quadtree
import pygame as pg
import math
import sys
import random



display_res = []
ground = 705
frames_til_grounded = 100  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally - currently unused
EMPTY = 0
OCCUPIED = 1

class Matrix(dict):  #TODO: Use dict, looks like it is fastest. But maybe I can speed up the exception handling
    # __slots__ = dict
    def __init__(self, width: int, height: int):
        super().__init__()
        # self.matrix = {}
        for x in range(-10, width + 10):  # initalize all spaces as empty
            for y in range(-10, height + 10):
                self[x,y] = -1

    def get_val(self, key):
        try: return self[key]
        except KeyError: return None

    # def __getitem__(self, key):  # overrirde default to return None if out of bounds. Makes it slower
    #     # return self.get(key, None)
    #     try: return self[key]
    #     except KeyError: return None



class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int, game):
        self.blocks = set()
        self.inactive_blocks = set()
        self.destroyable_blocks = set()
        self.unground_frame_blocks = set()  # blocks that will become ungrounded at end of frame
        sys.setrecursionlimit(99999)  # increased to allow ungrounding
        self.unground_count = 0
        self.all_blocks = []  # do not remove from list so indices stay the same
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        self.first_trigger_radius = 10
        self.gravity = 1
        self.terminal_velocity = 1
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.quadtree = Quadtree(self.screen_width, self.screen_height)
        self.matrix = Matrix(width=screen_width + 10, height=screen_height+10)
        # self.matrix = {}
        # for x in range(-10, screen_width + 10):  # initalize all spaces as empty
        #     for y in range(-10, screen_height + 10):
        #         self.matrix[x,y] = (0, None)
        # print(f'matrix length: {len(self.matrix)}')



    def setup(self, render_image):
        self.render_image = render_image

    def fill_matrix(self):  # will need new method for adding blocks after init
        for i, b in enumerate(self.all_blocks):
            b.id = i
            self.matrix[b.position[0], b.position[1]] = b.id



    def update(self, screen) -> None:
        for block in self.blocks:
            self.update_blocks(block=block, screen=self.render_image)

        self.inactive_blocks.update({b for b in self.blocks if not b.collision_detection})
        self.blocks = {b for b in self.blocks if b.collision_detection}
        self.end_frame_unground()
        # print(len([b for b in self.blocks]))
        # print(len(self.blocks))





# Physics

    # TODO: Need to ravamp this for speed changes
    def check_under(self, position: (int, int)) -> bool:
        if position[1] == ground:
            return True
        return self.matrix.get_val((position[0], position[1] + 1)) != -1


    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        # if self.screen_width > block.position[0] + dir > 0 \  # costs fps
        #   and self.screen_height > block.position[1] + dir > 0:
        if self.matrix.get_val((block.position[0] + dir, block.position[1] + 1)) == -1:  # EMPTY:
            return dir
        elif self.matrix.get_val((block.position[0] - dir, block.position[1] + 1)) == -1:  # EMPTY:
            return -dir
        return 0

    def check_slope(self, position: (int, int), direction: int) -> bool:
        if self.matrix.get_val((position[0] + direction[0], position[1] - 1)) == -1:  # EMPTY:
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
        self.matrix[block.position[0], block.position[1]] = -1
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0], block.position[1] + block.vert_velocity)
#TODO: If want to incorporate block width/height, need to draw all pixels contained here
#That adds complexity to 1-width blocks, though
        self.matrix[block.position[0], block.position[1]] = block.id  # OCCUPIED
        return


    def slide(self, block: Block, slide: int) -> None:
        block.horiz_velocity = slide * 1 * slide_factor
        self.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0] + block.horiz_velocity, block.position[1])
        self.matrix[block.position[0], block.position[1]] = block.id
        return


    def destroy_block(self, block: Block) -> None:
        self.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.game.spaces_to_clear.add(block.position)
        # Now check all spaces around this block for ungroundable blocks. Note this will be called for all
        # blocks in the destruction zone
        self.trigger_ungrounding(block)



#TODO: Iterating through this many times for the same particle
    def trigger_ungrounding(self, block: Block) -> None:
        for x in range(-1, 2):
            for y in range(-1, 2):
                pos = (block.position[0] + x, block.position[1] + y)
                unground_block = self.all_blocks[self.matrix[pos]]
                # self.unground_count += 1
                if not unground_block.type.rigid and not unground_block.collision_detection:
                    unground_block.collision_detection = True
                    self.unground_frame_blocks.add(unground_block)
                    self.trigger_ungrounding(unground_block)


    def end_frame_unground(self) -> None:
        for block in self.unground_frame_blocks:
            block.grounded_timer = 0
            self.blocks.add(block)
            self.inactive_blocks.remove(block)
        # if len(self.unground_frame_blocks) > 0:
        #     print(f'block count: {len(self.unground_frame_blocks)}')
        self.unground_frame_blocks.clear()
        # if self.unground_count != 0:  # roughly 10x the # of actual blocks to unground
        #     print(f'unground count: {self.unground_count}')



# Quadtree structure used for destroyable particles only, to find particles within destroy radius
    def initialize_quadtree(self) -> (set[Quadtree_Node], bool):
        if self.quadtree.initialized:
            return self.quadtree.all_quads, False
        else:
            insert_blocks = {b for b in self.blocks if b.type.destroyable}  # only insert destroyable blocks
            print(f'quadtree particle insert count: {len(insert_blocks)}')
            # as blocks are always active upon load, then switch to inactive.
            return self.quadtree.create_tree(insert_blocks), True

    def insert_object_quadtree(self, obj, x: int, y: int) -> Quadtree_Node:  # use to put specific position in tree
        return self.quadtree.insert_object(obj=obj, x=x, y=y, start_node=self.quadtree.root_node)
        # now can access node.children to get neighboring objects
