from Blocks.block import Block
import Blocks.block_type as block_type
from quadtree import Quadtree_Node, Quadtree
import pygame as pg
import math
import sys
import random



display_res = []
ground = 705
frames_til_grounded = 150  # how many frames a block must be stationary before being grounded
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
                self[x,y] = (0, None)

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
        self.quadtree_creation_time = 99



    def setup(self, render_image):  # need new method for adding blocks after init
        for b in self.blocks:
            self.matrix[b.position[0], b.position[1]] = OCCUPIED
        self.render_image = render_image


    # @profile
    def update(self, screen) -> None:
        self.quadtree_creation_time += 1
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
        return self.matrix.get_val((position[0], position[1] + 1)) == 1


    def check_slide(self, block) -> int:  # int -1 for slide left, 1 slide right, 0 no slide
        dir = 1 if random.random() < 0.5 else -1
        # if self.screen_width > block.position[0] + dir > 0 \  # costs fps
        #   and self.screen_height > block.position[1] + dir > 0:
        if self.matrix.get_val((block.position[0] + dir, block.position[1] + 1)) == EMPTY:
            return dir
        elif self.matrix.get_val((block.position[0] - dir, block.position[1] + 1)) == EMPTY:
            return -dir
        return 0

    def check_slope(self, position: (int, int), direction: int) -> bool:
        if self.matrix.get_val((position[0] + direction[0], position[1] - 1)) == EMPTY:
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
        self.matrix[block.position[0], block.position[1]] = (OCCUPIED, block)
        return


    def destroy_block(self, block: Block) -> None:
        self.matrix[block.position[0], block.position[1]] = EMPTY
        self.game.spaces_to_clear.add(block.position)



    def trigger_ungrounding(self, node: Quadtree_Node, position: (int, int) = (0,0), call_count: int = 0):
        # call_count += 1
        triggered = False
        node.ungrounded = True
        # Create the quadtree and insert all particles if not rigid / not in inactive_blocks
        quad_nodes, reinitialized = self.initialize_quadtree()
        # need to recreate in case blocks moved... Timer determines
        # how to avoid, or limit # of blocks to insert?
        if reinitialized:
            self.game.quadtree_nodes = quad_nodes

#TODO: Only insert blocks in the same node as the position variable if creating a new quadtree at runtime
# just branch down into the same branches as the position


        # Now unground all blocks inside the nodes. if find blocks continue to branch UP
        objs = node.objects
        for child in node.children:  # if node has children means we worked up 1 branch, so hit children of that parent
            objs.update(child.objects)
        print(f'adding {len(objs)}')
        for block in objs:
            if block.type.rigid or block not in self.inactive_blocks:
                continue
            self.unground_recursive_check(block)
            # block.collision_detection = True
            # block.grounded_timer = 0
            # self.blocks.add(block)
            # self.inactive_blocks.remove(block)
            # triggered = True

    def unground_recursive_check(self, block):
        block.collision_detection = True
        block.grounded_timer = 0
        self.blocks.add(block)
        self.inactive_blocks.remove(block)
        if self.matrix[block.position[0], block.position[1] + 1] == OCCUPIED:
            # Now get the quadtree objects at that location?
            # Need to ensure I don't trigger when a block is in a node that has already been returned
            node = self.insert_object_quadtree(None, block.position[0], block.position[1] + 1)
            if not node.ungrounded:
                self.trigger_ungrounding(node=node)
        if self.matrix[block.position[0], block.position[1] - 1] == OCCUPIED:
            # Now get the quadtree objects at that location?
            # Need to ensure I don't trigger when a block is in a node that has already been returned
            node = self.insert_object_quadtree(None, block.position[0], block.position[1] - 1)
            if not node.ungrounded:
                self.trigger_ungrounding(node=node)
        if self.matrix[block.position[0] + 1, block.position[1]] == OCCUPIED:
            # Now get the quadtree objects at that location?
            # Need to ensure I don't trigger when a block is in a node that has already been returned
            node = self.insert_object_quadtree(None, block.position[0] + 1, block.position[1])
            if not node.ungrounded:
                self.trigger_ungrounding(node=node)
        if self.matrix[block.position[0] - 1, block.position[1]] == OCCUPIED:
            # Now get the quadtree objects at that location?
            # Need to ensure I don't trigger when a block is in a node that has already been returned
            node = self.insert_object_quadtree(None, block.position[0] - 1, block.position[1])
            if not node.ungrounded:
                self.trigger_ungrounding(node=node)







        # radius = self.first_trigger_radius * call_count
        # for y in range(position[1]-radius, position[1]+radius):
        #     for x in range(position[0]-radius, position[0]+radius):
        #         if y < 0 or x < 0 or y > self.screen_height or x > self.screen_width:
        #             continue
        #         # print(f'checking {x}  {y}')
        #         check_pos = (x, y)
        #         block = self.matrix[check_pos[0], check_pos[1]]
        #         if not block or block.type.rigid or block not in self.inactive_blocks:
        #             continue
        #         block.collision_detection = True
        #         block.grounded_timer = 0
        #         self.blocks.add(block)
        #         self.inactive_blocks.remove(block)
        #         triggered = True
        #
        # if triggered:
        #     self.trigger_ungrounding(position=position, call_count=call_count)


#TODO need to redo the branches for particles that moved since creation
    def initialize_quadtree(self) -> (set[Quadtree_Node], bool):
        if self.quadtree.initialized and self.quadtree_creation_time < 120:
            return self.quadtree.all_quads, False
        else:
            # ungroundable_blocks = [b for b in self.inactive_blocks if not b.type.rigid]
            insert_blocks = {b for b in self.blocks if not b.type.rigid or b.type.destroyable}
            insert_blocks.update(b for b in self.inactive_blocks if not b.type.rigid)  # currently not needed
            print(f'quadtree particle insert count: {len(insert_blocks)}')
            # as blocks are always active upon load, then switch to inactive.
            self.quadtree_creation_time = 0
            return self.quadtree.create_tree(insert_blocks), True


    def insert_object_quadtree(self, obj, x: int, y: int) -> Quadtree_Node:  # use to put specific position in tree
        return self.quadtree.insert_object(obj=obj, x=x, y=y, start_node=self.quadtree.root_node)
        # now can access node.children to get neighboring objects

