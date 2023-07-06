# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree
import pygame as pg
import math

class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.root_quads = []
        self.all_quads = set()
        self.blocks = []
        self.block_rects = []
        # 2d array representing the spatials organization of the quadtrees. Used to quickly assess block location
        # self.tree_org = []
        # New idea: first block that builds quadtree nieghbors sends the list here
        # self.q_neighbors = dict()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_branches = 6
        self.capacity = 16

    # def organize_trees(self, quadtrees: list[Quadtree]):
    #     for tree in quadtrees:
    #         if tree.x == 0.0:
    #             self.tree_org.append([])
    #         self.tree_org[-1].append(tree)
    #     # trees now arranged in 2d array of size y_count * x_count



#TODO: Instead of quadtrees keeping track of their neighbors, blocks that cross multiple quadtrees can
# give themselves to both leaves, so they are detected in collisions for either leaf
# this will be lower cost since many fewer blocks in collision detection

    def update(self, screen) -> list:
        self.all_quads = set()  # just for drawing visually
        # self.update_quadtrees()

        # blocks update to a new quadtree if they leave their current tree
        # [self.update_block_quadtree(block=block)
        #  for block in self.blocks if block.collision_detection]

        root_quadtree = Quadtree(x=0, y=0 + self.screen_height,
                                 width=self.screen_width, height=self.screen_height, branch_count=0)
        [self.insert_blocks(block, root_quadtree) for block in self.blocks]

        # self.update_quad_neighbors()

        for block in self.blocks:
            block.update(screen=screen)

        # print(f'{len(self.all_quads)} all quads')
        return self.all_quads


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



    def find_leaf(self, block, quadtree):  # recursively move out toward leaves
        if quadtree.branch_count == self.max_branches:
            # or 0 < len(quadtree.objects) < self.capacity: # doesn't work does it? what about for later blocks
            self.all_quads.add(quadtree)
            # return quadtree
            block.leaves.append(quadtree)
        else:
            children = quadtree.create_branches(quadtree.branch_count)
            # determine which child contains the block
            for child in children:
                contained = self.check_block_in_quad(block, child)
                if contained:
                    # return self.find_leaf(block, child)
                    self.find_leaf(block, child)



    def get_neighbors(self, quadtree):
        return quadtree.get_neighbors()


    # def get_update_neighbors(self, quadtree):
    #     if quadtree in self.q_neighbors:
    #         return self.q_neighbors[quadtree]
    #     neighbors = quadtree.get_neighbors()
    #     self.q_neighbors[quadtree] = neighbors
    #     return neighbors


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
        # if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
        #     and quadtree.y >= block.rect.centery >= quadtree.y - quadtree.height:
        #         return True
        else: return False


    def add_rects_to_quadtree(self, block, quadtree: Quadtree):
        # for quadtree in quadtrees:
            # if self.check_block_in_quad(block, quadtree):
        quadtree.objects.append(block)
        # block.quadtree = quadtree
            # self.quadtrees.append(quadtree)
        # new method: place blocks in tree based on x,y and self.tree_org indices
        # x_index = math.floor(block.rect.centerx / x_count)
        # y_index = math.floor(block.rect.centery / y_count)
        # tree = self.tree_org[y_index][x_index]
        # tree.objects.append(block)
        # block.quadtree = tree



# improvement: 1 option = only calling this for blocks with collision_detection = True
  # option 2 = starting with the Quadtree and only passing in blocks that are close + collision detection
    # Called every frame for blocks with collision detection True
    # def update_block_quadtree(self, block) -> None:  # , y_count: int, x_count: int
    #     # TODO: some blocks do not properly exit their quadtrees. The tree still has objects in its list
    #     # slower :(   32 fps lowest vs 39 fps
    #     # block.quadtree.objects.remove(block)
    #     # x_index = math.floor(block.rect.centerx / x_count)
    #     # y_index = math.floor(block.rect.centery / y_count)
    #     # tree = self.tree_org[y_index][x_index]
    #     # tree.objects.append(block)
    #     # block.quadtree = tree
    #     # return
    #
    #     try:
    #         x_change = block.rect.centerx - block.quadtree.x
    #         y_change = block.rect.centery - block.quadtree.y
    #     except:
    #         return
    #
    #     if y_change > block.quadtree.height and block.quadtree.south:
    #         block.quadtree.south.objects.append(block)
    #         block.quadtree = block.quadtree.south
    #         block.quadtree.objects.remove(block)
    #     elif x_change < 0 and block.quadtree.west:
    #         block.quadtree.west.objects.append(block)
    #         block.quadtree = block.quadtree.west
    #         block.quadtree.objects.remove(block)
    #     elif x_change > block.quadtree.width and block.quadtree.east:
    #         block.quadtree.east.objects.append(block)
    #         block.quadtree = block.quadtree.east
    #         block.quadtree.objects.remove(block)
    #     elif y_change < 0 and block.quadtree.north:  # assign north
    #         block.quadtree.north.objects.append(block)
    #         block.quadtree = block.quadtree.north
    #         block.quadtree.objects.remove(block)