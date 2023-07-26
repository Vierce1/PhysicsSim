from Blocks.block import Block, Trail
import Blocks.block_type as block_type
from quadtree import Quadtree_Node, Quadtree
import pygame as pg
import math
import sys
import random
from collections import defaultdict
import multiprocessing.dummy as mp
# from multiprocessing import Pool
from threading import Thread
import asyncio
from numba import jit


display_res = []
frames_til_grounded = 1  # how many frames a block must be stationary before being grounded
slide_factor = 1  # how fast blocks slide horizontally - currently unused
# EMPTY = 0
# OCCUPIED = 1

class Matrix(defaultdict):  # defaultdict will create items if try to get a value from a key that does not exist
    def __init__(self, width: int, height: int):
        super().__init__(self.default)  # will return -1 for out of bounds (fall)
        # self.matrix = {}
        for x in range(width):  # initalize all spaces as empty
            for y in range(height):
                self[x,y] = -1

    def default(self):
        return -1



class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int, game):
        self.blocks = set()
        # self.inactive_blocks = set()
        self.destroyable_blocks = set()
        self.unground_pos_checks = set()
        self.all_blocks = []  # do not remove from list so indices stay the same
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.render_image = None
        self.first_trigger_radius = 10
        self.gravity = 1
        self.terminal_velocity = 20
        self.ground = 1200  # redefined by level
        self.wind = 0  # redefined by level
        self.matrix = Matrix(width=0, height=0)
        self.quadtree = Quadtree(0, 0)
        self.random_bits = []
        # self.pool = mp.Pool()
        self.time_count_avgs = []


    def setup(self, render_image, world_size: (int, int), ground_level: int):
        self.render_image = render_image
        self.matrix = Matrix(width=world_size[0], height=world_size[1])
        self.quadtree = Quadtree(world_size[0], world_size[1])
        self.ground = ground_level
        self.wind = self.game.environ.get_wind()
        self.blocks.clear()
        self.all_blocks.clear()
        self.destroyable_blocks.clear()
        # Fill ground w/ -2
        for x in range(world_size[0]):
            for y in range(self.ground, world_size[1]):
                self.matrix[x, y] = -2

    def fill_matrix(self):  # will need new method for adding blocks after init
        for i, b in enumerate(self.all_blocks):
            b.id = i
            self.matrix[b.position[0], b.position[1]] = b.id
        self.random_bits = [random.randrange(0, 2) for _ in range(len(self.blocks))]
        self.blocks = {block.id for block in self.blocks}
        print(f'length = {len(self.blocks)}')

    def add_blocks_to_matrix(self, particles: list[Block]):
        for p in particles:
            p.id = len(self.all_blocks)
            self.matrix[p.position[0], p.position[1]] = p.id
            if self.game.block_type_list[p.type].destroyable:
                self.destroyable_blocks.add(p)
            self.blocks.add(p.id)  # have to add ALL blocks to this first so they draw on frame 1
            self.all_blocks.append(p)
        self.random_bits.extend([random.randrange(0, 2) for _ in range(len(particles))])


    async def update(self) -> None:
        # self.time_count_avgs.clear()

        for block_id in list(self.blocks):  # use a copy of the set for safe multi threading
            await self.update_blocks(block_id=block_id)

        # if len(self.time_count_avgs) > 0:  # Timing block falling
        #     average = 0
        #     for t in self.time_count_avgs:
        #         average += t
        #     average /= len(self.time_count_avgs)
        #     print(f'average: {average}')
        # print(f'\t\t\t\t\t\t\t\t\tactive block count: {len(self.blocks)}')
        # print(f'\t\t\t\t\t\t\t\t\t\tinactive block count: {len(self.inactive_blocks)}')





# Particle physics
    def check_pos_collide(self, x: int, y: int) -> bool:
        return self.matrix[x,y] != -1


    def check_under_player(self, position: (int, int)) -> bool:
        if position[1] == self.ground:
            return True
        return self.matrix[(position[0], position[1] + 1)] != -1

    # def chain_fall_check(self, x: int, y: int) -> int:  # , y_vel: int
    #     for i in range(1, 11):
    #         block_id = self.matrix[x, y + i]
    #         if block_id == -1:
    #             continue


#TODO: Convert the all_blocks list to a custom python object (list)
# and on error return None to eliminate the extra step


#TODO: The shallower a block type's slide grade is, the more blocks get eaten...
    def check_slope(self, block_id: int, b_type: int, position: (int, int)) -> int:
        # returns int -1 for slide left, 1 slide right, 0 no slide
        under_block_id = self.matrix[position[0], position[1] + 1]
        under_block = self.all_blocks[under_block_id]
        if under_block.sliding:
            return 0
        direction = 1 if self.random_bits[block_id] == 1 else -1  # Improvement?
        slide_grade = self.game.block_type_list[b_type].slide_grade
        x, y = position[0] + direction * slide_grade[0], position[1] + slide_grade[1]
        if self.matrix[x,y] == -1:  # Do i need to check the spaces beteen block and the slide grade check spot?
            return direction
        else:  # check other direction
            x = position[0] - direction * slide_grade[0]
            if self.matrix[x, y] == -1:
                return -direction
            else:
                return 0


    def check_liquid_flow(self, block_id: int, position: (int, int)):
        # returns int -1 for flow left, 1 flow right, 0 no flow
        # Liquid: 0 y difference, ensure block below is liquid
        under_block_id = self.matrix[position[0], position[1] + 1]
        if under_block_id != -2:
            under_block = self.all_blocks[under_block_id]
            if self.game.block_type_list[under_block.type].liquid and not under_block.sliding:
                # Now check if the direction is good
                direction = 1 if self.random_bits[block_id] == 1 else -1  # Improvement?
                if self.matrix[position[0] + direction, position[1]] == -1:
                    return direction
                elif self.matrix[position[0] - direction, position[1]] == -1:
                    return -direction
        return 0


    def check_walk_slope(self, player_pos: (int, int), direction: int):
        if self.matrix[(player_pos[0] + direction[0], player_pos[1])] != -1 \
                and self.matrix[(player_pos[0] + direction[0], player_pos[1] - 1)] == -1:  # EMPTY:
            return True
        return False



    # Particle functions
    # @jit(nopython=True)
    async def update_blocks(self, block_id: int):
        block = self.all_blocks[block_id]
        b_type = self.game.block_type_list[block.type]
        if block.collision_detection:
            # if block.type == block_type.SAND:  # Timing block falling
            #     block.time_falling += 1 * self.game.physics_lag_frames
            #     self.time_count_avgs.append(block.time_falling)
            # Having this here ensures spaces get cleared properly
            out_of_bounds = self.game.spaces_to_clear.add_pos(block.position)
            if out_of_bounds:
                block.collision_detection = False

        #TODO: somehow a small # of blocks are remaining in the active list and not going into inactive list
    # try level 1.
            # update velocities
            if block.vert_velocity < self.terminal_velocity:
                block.vert_velocity += self.gravity

            if self.wind != 0 and abs(block.horiz_velocity) <= abs(self.wind / b_type.weight):
                block.horiz_velocity += 1  # Add wind step til hit max wind velocity
            elif block.horiz_velocity != 0:
                horiz_step = 1 if block.horiz_velocity > 0 else -1
                block.horiz_velocity -= horiz_step


            # move through all spaces based on velocity
    #TODO: Problems:
        #1. Blocks split into forks when lagging
        #2. Blocks still moving slow when lagging
            total_x = block.horiz_velocity * self.game.physics_lag_frames
            total_y = block.vert_velocity * self.game.physics_lag_frames
            # print(f'{block_id} total :  {total_x}  / {total_y}')
            # for _ in range(0, max(abs(total_y), abs(total_x))):
            while total_y != 0 or total_x != 0:
                # Get the next position to check. If game is lagging, skip some checks. Otherwise use -1/1
                next_x, next_y = self.get_step_velocity(total_x, total_y)
                # print(f'{block_id} :     {next_x} / {next_y}')
                collided = self.move(block.id, next_x, next_y)
                if collided:
                    break

                if total_x != 0:
                    if -1 < total_x / self.game.physics_lag_frames < 1:
                        total_x -= 1 if total_x > 0 else -1
                    else:
                        total_x -= self.game.physics_lag_frames if total_x > 0 else -self.game.physics_lag_frames
                if total_y != 0:
                    if -1 < total_x / self.game.physics_lag_frames < 1:
                        total_y -= 1 if total_y > 0 else -1
                    else:
                        total_y -= self.game.physics_lag_frames if total_y > 0 else -self.game.physics_lag_frames

            # Spawn particle trail
            # if not block.trail_created and abs(block.vert_velocity) > 0:
            #     block.trail_created = True
            #     self.create_trail(block_id)

        elif block.id in self.blocks:
            self.blocks.remove(block.id)

        if b_type.destructive:
            self.destructive(block, block.position[0], block.position[1])

        self.game.render_dict.add((block.position, b_type.get_color()))


    def move(self, block_id: int, x_step: int, y_step: int) -> bool:  # returns collided, to end the movement loop
        block = self.all_blocks[block_id]
        new_x, new_y = block.position[0] + x_step, block.position[1] + y_step
        collision = self.check_pos_collide(new_x, new_y)

        if collision:  # collided. Check if it should slide/flow to either side + down 1
            block.horiz_velocity = 0  # Ideally both axes would not necessarily go to zero
            block.vert_velocity = 0
            b_type = self.game.block_type_list[block.type]
            if b_type.liquid:
                slide = self.check_liquid_flow(block_id=block_id, position=block.position)
            else:
                slide = self.check_slope(block_id=block_id, b_type=block.type, position=block.position)
            if slide != 0:
                block.sliding = True
                block.horiz_velocity += slide  # Doesn't matter right now, adding more than 1 would
                old_pos = block.position[0], block.position[1]
                self.matrix[old_pos] = -1  # EMPTY
                # out_of_bounds = self.game.spaces_to_clear.add_pos(block.position)
                # if out_of_bounds:
                #     block.collision_detection = False
                # new_y = 0 if b_type.liquid else 1
                new_y = 0
                block.position = (block.position[0] + slide, block.position[1] + new_y)
                self.matrix[block.position[0], block.position[1]] = block.id
                self.trigger_ungrounding(block_id, old_pos)  # trigger ungrounding in previous position
            else:  # collided and is not sliding. Turn collision off
                if not b_type.destructive or (b_type.destructive and block.destroy_counter == -1):
                    block.collision_detection = False
                    block.sliding = False
            return True

        # Did not collide. Mark prev position empty & mark to fill with black
        old_pos = block.position[0], block.position[1]
        self.matrix[old_pos] = -1
        # if self.game.spaces_to_clear.add_pos(block.position):
        #     block.collision_detection = False   # went out of bounds. Could just draw a square around map to avoid this
        block.position = (new_x, new_y)
        self.matrix[block.position[0], block.position[1]] = block.id  # OCCUPIED
        self.trigger_ungrounding(block_id, old_pos)  # trigger ungrounding in previous position
        block.sliding = False
        return False


    def get_step_velocity(self, total_x: int, total_y: int) -> (int, int):
        # returns a position based on velocity, trimmed down to -1 to +1 in any direction
        x = total_x
        y = total_y
        if self.game.physics_lag_frames > 1:  # physics rendering lagging. Skip some checks
            if total_x > 1:
                x = min(self.game.physics_lag_frames, total_x)
            elif total_x < -1:
                x = max(self.game.physics_lag_frames, total_x)
            if total_y > 1:
                y = min(self.game.physics_lag_frames, total_y)
            elif total_y < -1:
                y = max(self.game.physics_lag_frames, total_y)
        else:
            if x < 0:
                x = -1
            elif x > 0:
                x = 1
            if y < 0:
                y = -1
            elif y > 0:
                y = 1
        return int(x), int(y)



    def create_trail(self, block_id: int):
        block = self.all_blocks[block_id]
        color = (min(self.game.block_type_list[block.type].color[0] + 65, 255),
                 min(self.game.block_type_list[block.type].color[0] + 65, 255),
                 min(self.game.block_type_list[block.type].color[0] + 65, 255))
        trail = Trail(parent_id=block_id, color=color)
        self.game.trails.add(trail)



# destructive blocks take a # of frames to destroy a neighboring block, based on their type
    def destructive(self, block: Block, x: int, y: int):
        block.destroy_counter += 1
        if block.destroy_counter >= self.game.block_type_list[block.type].destroy_count:
            block.destroy_counter = 0
            destroyed_count = 0
            for x in range(x-1, x+2):
                for y in range(y-1, y+2):
                    neighbor_id = self.matrix[x, y]
                    if neighbor_id >= 0 and neighbor_id != block.id:  # don't destroy ground or self
                        neighbor = self.all_blocks[neighbor_id]
                        if self.game.block_type_list[neighbor.type].destroyable:
                            self.destroy_block(neighbor_id)
                            destroyed_count += 1
            if destroyed_count == 0:  # no blocks destroyed, count it as grounded now
                block.destroy_counter = -1


    def destroy_block(self, block_id: int) -> None:
        block = self.all_blocks[block_id]
        self.matrix[block.position[0], block.position[1]] = -1  # EMPTY
        self.game.spaces_to_clear.add_pos(block.position)
        # Now check all spaces around this block for ungroundable blocks. Note this will be called for all
        # blocks in the destruction zone
        self.trigger_ungrounding(block_id, block.position)



#TODO: There may be more finetuning to reduce checks on same positions
# Can I move this to the main thread? Modifying the blocks in multiple places won't work, maybe there's a solution.
    def trigger_ungrounding(self, id: int, position: (int, int)) -> None:
        # Ungrounding should start from the lowest block so don't bother checking y > 0
        for x in range(-1, 2):
            for y in range(-2, 1):  # Updated from 2. Theoretically shouldn't need to check down
                check_pos = (position[0] + x, position[1] + y)
                # add the position to the set to check if there's an ungroundable block at end of sequence
                if check_pos != position:
                    block_id = self.matrix[check_pos]
                    if block_id < 0 or block_id == id:  # -1 or -2 for ground
                        continue
                    block = self.all_blocks[block_id]
                    # Keep the ungrounding split up over multiple frames for performance.
                    # When this now active block moves it will activate its neighbors the following frame
                    if not self.game.block_type_list[block.type].rigid and not block.collision_detection:
                        block.collision_detection = True
                        self.blocks.add(block_id)
                    # self.unground_pos_checks.add(check_pos)


    # def end_frame_unground(self) -> None:
    #     if len(self.unground_pos_checks) == 0:
    #         return
    #     for pos in self.unground_pos_checks:
    #         block_id = self.matrix[(pos)]
    #         if block_id == -1:
    #             continue
    #         block = self.all_blocks[block_id]
    #         if not block.type.rigid and not block.collision_detection:
    #             block.collision_detection = True
    #             self.blocks.add(block)
    #     # self.unground_pos_checks.clear()



# Quadtree structure used for destroyable particles only, to find particles within destroy radius
    def initialize_quadtree(self) -> (set[Quadtree_Node], bool):
        if self.quadtree.initialized:
            return self.quadtree.all_quads, False
        else:
            insert_blocks = set()
            for b in self.blocks:
                if self.game.block_type_list[self.all_blocks[b].type].destroyable:
                    insert_blocks.add(self.all_blocks[b])
            # insert_blocks = {self.all_blocks[b] for b in self.blocks if self.all_blocks[b].type.destroyable}
            # only insert destroyable blocks
            print(f'quadtree particle insert count: {len(insert_blocks)}')
            # as blocks are always active upon load, then switch to inactive.
            return self.quadtree.create_tree(insert_blocks), True

    def insert_object_quadtree(self, obj, x: int, y: int) -> Quadtree_Node:  # use to put specific position in tree
        return self.quadtree.insert_object(obj=obj, x=x, y=y, start_node=self.quadtree.root_node)
        # now can access node.children to get neighboring objects
