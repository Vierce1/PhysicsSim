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


#TODO: Instead of quadtrees keeping track of their neighbors, blocks that cross multiple quadtrees can
# give themselves to both leaves, so they are detected in collisions for either leaf
# this will be lower cost since many fewer blocks in collision detection

    def update(self, screen) -> list:
        self.all_quads = set()  # just for drawing visually

        root_quadtree = Quadtree(x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height, branch_count=0)
        [self.insert_blocks(block, root_quadtree) for block in self.blocks]

        for block in self.blocks:
            block.update(screen=screen)

        # print(f'{len(self.all_quads)} all quads')
        return self.all_quads

    #TODO: Now collision detection is very efficient, but creating nodes every frame slow
# Need a way to skip this for grounded blocks.
# For grounded blocks can I cache the position of their quadtree and then add them in after the other blocks finish?
    def insert_blocks(self, block, root_quadtree):
        block.leaves = []
        self.find_leaf(block, root_quadtree)
        for leaf in block.leaves:
            self.add_rects_to_quadtree(block, leaf)



    def find_leaf(self, block, quadtree):  # recursively move out toward leaves
        if quadtree.branch_count == self.max_branches:
            # or 0 < len(quadtree.objects) < self.capacity: # doesn't work does it? what about for later blocks
            self.all_quads.add(quadtree)
            # return quadtree
            block.leaves.append(quadtree)
        else:
            children = self.create_branches(quadtree)
            # determine which child contains the block
            for child in children:
                contained = self.check_block_in_quad(block, child)
                if contained:
                    # return self.find_leaf(block, child)
                    self.find_leaf(block, child)


    def create_branches(self, quadtree: Quadtree):
        if len(quadtree.children) > 0:
            return quadtree.children  # another block already created the children

        # node children not created yet. Make them.
        for i in range(2):
            for j in range(2):
                child = Quadtree(x=quadtree.x + j * quadtree.width * 0.5, y=quadtree.y - i * quadtree.height * 0.5,
                                 width=quadtree.width * 0.5, height=quadtree.height * 0.5,
                                 branch_count=quadtree.branch_count + 1)
                quadtree.children.append(child)
        return quadtree.children


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

        # q_width, q_height = self.get_quadnode_dimensions(quadtree.branch_count)
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
        quadtree.objects.append(block)


    # def get_quadnode_dimensions(self, branch_count):
    #     divisor = 1
    #     if branch_count > 0:
    #         # divisor = math.pow(branch_count + 1, 2) / 2
    #         divisor = (2 ** (branch_count + 1)) / 2
    #
    #     q_width = self.screen_width / divisor
    #     q_height = self.screen_height / divisor
    #     return q_width, q_height