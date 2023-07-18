from Blocks.block import Block
import Blocks.block_type as block_type
from quadtree import Quadtree_Node, Quadtree
import pygame as pg
import math
import sys
import random
from collections import defaultdict


display_res = []
ground = 705
frames_til_grounded = 400  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally - currently unused
# EMPTY = 0
# OCCUPIED = 1

class Matrix(defaultdict):  # defaultdict will create items if try to get a value from a key that does not exist
    def __init__(self, width: int, height: int):
        super().__init__(self.default)  # will return -1 for out of bounds (fall)
        # self.matrix = {}
        for x in range(-10, width + 10):  # initalize all spaces as empty. Buffer for offscreen falling (temp)
            for y in range(-10, height + 10):
                self[x,y] = -1

    def default(self):
        return -1



class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int, game):
        self.blocks = set()
        self.inactive_blocks = set()
        self.destroyable_blocks = set()
        self.unground_pos_checks = set()
        self.current_unground_chain_checks = set()  # Set to keep track of pos already checked this chain
        self.all_blocks = []  # do not remove from list so indices stay the same
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        self.first_trigger_radius = 10
        self.gravity = 1
        self.terminal_velocity = 20
        self.matrix = Matrix(width=0, height=0)
        self.quadtree = Quadtree(0, 0)
        self.booly = False


    def setup(self, render_image, world_size: (int, int)):
        self.render_image = render_image
        self.matrix = Matrix(width=world_size[0], height=world_size[1])
        self.quadtree = Quadtree(world_size[0], world_size[1])
        self.blocks.clear()
        self.all_blocks.clear()
        self.inactive_blocks.clear()
        self.destroyable_blocks.clear()

    def fill_matrix(self):  # will need new method for adding blocks after init
        for i, b in enumerate(self.all_blocks):
            b.id = i
            self.matrix[b.position[0], b.position[1]] = b.id



    def update(self) -> None:
        # if not self.booly:
        for block in self.blocks:
            self.update_blocks(block=block, render_surface=self.render_image)
            # self.booly = True

        # coll_blocks = set(filter(lambda b: b.collision_detection, self.blocks))
        # self.inactive_blocks.difference_update(self.blocks, coll_blocks)
        self.inactive_blocks.update({b for b in self.blocks if not b.collision_detection})
        # self.blocks = self.inactive_blocks.difference(coll_blocks)
        self.blocks = {b for b in self.blocks if b.collision_detection}
        self.end_frame_unground()
        # print(len(self.blocks))





# Physics
    def check_pos_collide(self, position: (int, int)) -> bool:
        if position[1] == ground:
            return True
        return self.matrix[position] != -1


#TODO: Remove and change player to use check_pos_collide
    def check_under(self, position: (int, int)) -> bool:
        if position[1] == ground:
            return True
        return self.matrix[(position[0], position[1] + 1)] != -1


#TODO: Somehow sand can overwrite dirt when flowing down a slope and hitting the sloped ceiling
    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        if self.matrix[(block.position[0] + dir, block.position[1] + 1)] == -1:  # EMPTY:
            return dir
        elif self.matrix[(block.position[0] - dir, block.position[1] + 1)] == -1:  # EMPTY:
            return -dir
        return 0

    def check_slope(self, position: (int, int), direction: int) -> bool:
        if self.matrix[(position[0] + direction[0], position[1])] != -1 \
                and self.matrix[(position[0] + direction[0], position[1] - 1)] == -1:  # EMPTY:
            return True
        return False





    # Particle functions
    def update_blocks(self, block, render_surface):
        # if block.grounded_timer > 0:
        #     print(f'grounded: {block.grounded_timer}')
        if block.collision_detection:
            if block.grounded_timer >= frames_til_grounded:
                block.collision_detection = False
                self.inactive_blocks.add(block)

            # update velocities
            if block.vert_velocity < self.terminal_velocity:
                block.vert_velocity += self.gravity
            if block.horiz_velocity != 0:
                block.horiz_velocity -= int(block.horiz_velocity / abs(block.horiz_velocity))

            # move through all spaces based on velocity
            total_x = block.horiz_velocity
            total_y = block.vert_velocity
            for _ in range(max(abs(block.vert_velocity) + 1, abs(block.horiz_velocity) + 1)):
                next_x, next_y = self.get_step_velocity(total_x, total_y)
                self.move(block, next_x, next_y)
                total_x -= total_x / abs(total_x) if total_x != 0 else 0  # decrement by 1 in correct direction
                total_y -= total_y / abs(total_y) if total_y != 0 else 0  # but stop if it gets to zero

            if block.vert_velocity == 0:
                block.grounded_timer += 1  # Increment grounded timer to take inactive blocks out of set

        render_surface.set_at(block.position, block.type.color)


    def move(self, block: Block, x_step: int, y_step: int) -> None:
        if block.position[1] == ground - 1:
            block.horiz_velocity = 0
            return
        next_pos = (block.position[0] + x_step, block.position[1] + y_step)
        collision = self.check_pos_collide(next_pos)
        # collision = self.check_under(block.position)  # no horiz motion considered
        if collision:  # collided. Check if it should slide to either side + down 1
            block.horiz_velocity = 0  # Ideally both axes would not necessarily go to zero
            block.vert_velocity = 0
            slide = self.check_slide(block)
            if slide != 0:
                self.slide(block, slide)
            return
        # Did not collide. Mark prev position empty & mark to fill with black
        self.matrix[block.position[0], block.position[1]] = -1
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0], block.position[1] + 1)
        self.matrix[block.position[0], block.position[1]] = block.id  # OCCUPIED
        return


    def get_step_velocity(self, total_x: int, total_y: int) -> (int, int):
        # returns a position based on velocity, trimmed down to -1 to +1 in any direction
        x = total_x
        y = total_y
        if x < 0:
            x = -1
        elif x > 0:
            x = 1
        if y < 0:
            y = -1
        elif y > 0:
            y = 1

        return x, y



    def slide(self, block: Block, slide: int) -> None:
        # block.horiz_velocity = slide * slide_factor  # don't add velocity. Don't need it and it causes issues
        self.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.game.spaces_to_clear.add(block.position)  # Slower with more particles updating
        block.position = (block.position[0] + slide, block.position[1])
        self.matrix[block.position[0], block.position[1]] = block.id
        return


    def destroy_block(self, block: Block) -> None:
        self.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.game.spaces_to_clear.add(block.position)
        # Now check all spaces around this block for ungroundable blocks. Note this will be called for all
        # blocks in the destruction zone
        self.trigger_ungrounding(block)



#TODO: There may be more finetuning to reduce checks on same positions
    def trigger_ungrounding(self, block: Block) -> None:
        # Ungrounding should start from the lowest block so don't bother checking y > 0
        for x in range(-1, 2):
            for y in range(-1, 1):  # Updated from 2. Theoretically shouldn't need to check down
                pos = (block.position[0] + x, block.position[1] + y)
                # add the position to the set to check if there's an ungroundable block at end of sequence
                if pos not in self.current_unground_chain_checks:  # did we check it already this chain?
                    self.unground_pos_checks.add(pos)
                self.current_unground_chain_checks.add(pos)


    def end_frame_unground(self) -> None:
        unground_frame_blocks = self.get_unground_blocks()
        if not unground_frame_blocks:
            self.current_unground_chain_checks.clear()  # Flush set, chain is complete.
            # self.unground_count = 0
            return
        next_frame_ungrounds = set()
        for block in unground_frame_blocks:
            block.grounded_timer = 0
            self.blocks.add(block)
            self.inactive_blocks.remove(block)
            next_frame_ungrounds.add(block)
        # if len(unground_frame_blocks) > 0:
        #     print(f'unground this frame block count: {len(unground_frame_blocks)}')
        for block in next_frame_ungrounds:  # now add the blocks to check next frame
            self.trigger_ungrounding(block)
        # if self.unground_count != 0:  # now only checking each block 1x
        #     print(f'unground count: {self.unground_count}')


#TODO: A block becomes ungrounded. Then grounded. Then another one next to it turns it back to ungrounded.#
# Does this happen, and if so do I want it to happen?
    def get_unground_blocks(self) -> set[Block] or None:
        if len(self.unground_pos_checks) == 0:
            return None
        unground_blocks = set()
        for pos in self.unground_pos_checks:
            # self.unground_count += 1
            block_id = self.matrix[(pos)]
            if block_id == -1:
                continue
            block = self.all_blocks[block_id]
            # print(f'pos to CHECK {pos}.    Block id = {self.matrix.get_val(pos)}')
            if not block.type.rigid and not block.collision_detection:
                block.collision_detection = True
                unground_blocks.add(block)
        self.unground_pos_checks.clear()
        return unground_blocks



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
