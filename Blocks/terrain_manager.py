# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
import physics
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree  #, QuadtreeElement
import pygame as pg
import math

class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.root_quads = []
        self.all_nodes = []
        self.node_count = 1  # for root node
        self.blocks = []
        self.block_rects = []
        # 2d array representing the spatials organization of the quadtrees. Used to quickly assess block location
        # self.tree_org = []
        # New idea: first block that builds quadtree nieghbors sends the list here
        self.q_neighbors = dict()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_branches = 6
        self.capacity = 16
        physics.terrain_manager = self


    def assign_block_indices(self):  # need new method for adding blocks after init
        [b.set_index(self.blocks.index(b)) for b in self.blocks]
        # for i in range(len(self.blocks)):
        #     self.blocks[i].set_index = i



#TODO: Instead of quadtrees keeping track of their neighbors, blocks that cross multiple quadtrees can
# give themselves to both leaves, so they are detected in collisions for either leaf
# this will be lower cost since many fewer blocks in collision detection

    def update(self, screen) -> list:
        self.all_nodes.clear()
        self.node_count = 1

        root_quadtree = Quadtree(id=0, x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height, branch_count=0)
        self.all_nodes.append(root_quadtree)

        [self.insert_blocks(block, root_quadtree) for block in self.blocks]

        for block in self.blocks:
            block.update(screen=screen)

        # print(f'{len(self.all_nodes)} all quads')
        return self.all_nodes


#TODO: Now collision detection is very efficient, but creating nodes every frame slow
# Need a way to skip this for grounded blocks.
# For grounded blocks can I cache the position of their quadtree and then add them in after the other blocks finish?
    def insert_blocks(self, block, root_quadtree):
        block.leaves = []
        # block.quadtrees = []
        # leaf = self.find_leaf(block, root_quadtree)
        self.find_leaf(block, root_quadtree)
        for leaf in block.leaves:
            self.add_rects_to_quadtree(block, leaf)



    def find_leaf(self, block, quadtree: Quadtree):  # recursively move out toward leaves
        if quadtree.branch_count == self.max_branches: # \
            block.leaves.append(quadtree)
        else:
            first_child = self.create_branches(quadtree=quadtree, branch_count=quadtree.branch_count,
                                            next_id=self.node_count)
            # determine which child(s) contains the block
            for i in range(first_child, first_child + 4):
                node = self.all_nodes[i]
                contained = self.check_block_in_quad(block, node)
                if contained:
                    # return self.find_leaf(block, child)
                    self.find_leaf(block, node)


    def create_branches(self, quadtree: Quadtree, branch_count: int, next_id: int):
        if quadtree.first_child != -1:
            return quadtree.first_child  # another block already created the children

        # node children not created yet. Make them.
        quadtree.first_child = next_id
        for i in range(2):
            for j in range(2):
                child = Quadtree(id=next_id,
                                 x=quadtree.x + j * quadtree.width * 0.5, y=quadtree.y - i * quadtree.height * 0.5,
                                 width=quadtree.width * 0.5, height=quadtree.height * 0.5,
                                 branch_count=branch_count + 1)
                self.all_nodes.append(child)
                next_id += 1
        self.node_count += 4
        return quadtree.first_child


    def get_neighbors(self, quadtree):  # Now returns indices of blocks
        # return [element.id for element in quadtree.objects]
        return quadtree.objects


    def check_block_in_quad(self, block, quadtree) -> bool:
        # Updated to have a buffer. Blocks added to multiple quadtree nodes if they are close to the border
        # FPS hit, but better than quadtrees keeping track of their neighbors
        right = block.rect.right + (1 * block.rect.width)
        left = block.rect.left - (1 * block.rect.width)
        top = block.rect.top + (1 * block.rect.height)
        bottom = block.rect.bottom - (1 * block.rect.height)
        if (right >= quadtree.x and left <= quadtree.x + quadtree.width) \
            and (bottom <= quadtree.y and top >= quadtree.y - quadtree.height):
                return True
        # Single node method:
        # if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
        #     and quadtree.y >= block.rect.centery >= quadtree.y - quadtree.height:
        #         return True
        else: return False


    def add_rects_to_quadtree(self, block, quadtree: Quadtree):
        # Could just do the block id and not build a new object
        # element = QuadtreeElement(x=block.rect.x, y=block.rect.y, id=block.index)
        quadtree.objects.append(block.index)
