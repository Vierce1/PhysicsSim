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
        self.all_quads = []
        self.blocks = []
        self.block_rects = []
        # 2d array representing the spatials organization of the quadtrees. Used to quickly assess block location
        self.tree_org = []
        # New idea: first block that builds quadtree nieghbors sends the list here
        # self.q_neighbors = dict()
        self.screen_width = screen_width
        self.screen_height = screen_height

    # def organize_trees(self, quadtrees: list[Quadtree]):
    #     for tree in quadtrees:
    #         if tree.x == 0.0:
    #             self.tree_org.append([])
    #         self.tree_org[-1].append(tree)
    #     # trees now arranged in 2d array of size y_count * x_count



    def update(self, screen) -> list:
        self.all_quads = []  # just for drawing visually
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

        print(f'{len(self.all_quads)} all quads')
        return self.all_quads



    def insert_blocks(self, block, root_quadtree):
        leaf = self.find_leaf(block, root_quadtree)
        self.add_rects_to_quadtree(block, [leaf])


#TODO: We don't want to create nodes that already were created by other blocks
    def find_leaf(self, block, quadtree):  # recursively move out toward leaves
        if quadtree.branch_count == 4:
            self.all_quads.append(quadtree)
            return quadtree
        children = quadtree.create_branches(quadtree.branch_count)
        # determine which child contains the block
        for child in children:
            contained = self.check_block_in_quad(block, child)
            if contained:
                return self.find_leaf(block, child)





    def update_quadtrees(self):
        # start with root nodes
        for q in self.root_quads:
            for child in q.children:  # start by deleting all children
                del child
                q.children.clear()

            empty = True
            for block in self.blocks:
                if self.check_block_in_quad(block, q):
                    self.recursive_update_quadtrees(quadtree=q)
                    empty = False
                    break  # found at least 1 block in quad, break for this quad
            if empty: # quadtree does not contain any blocks. Delete children
                for child in q.children:
                    del child
                    q.children.clear()


    def update_quad_neighbors(self):
        for quadtree in self.all_quads:
            quadtree.north = \
                next(iter([q for q in self.all_quads if q.y == quadtree.y - q.height and q.x == quadtree.x]),
                                  None)
            quadtree.south = \
                next(iter([q for q in self.all_quads if q.y == quadtree.y + q.height and q.x == quadtree.x]),
                                  None)
            quadtree.east = \
                next(iter([q for q in self.all_quads if q.x == quadtree.x + q.width and q.y == quadtree.y]),
                                 None)
            quadtree.west = \
                next(iter([q for q in self.all_quads if q.x == quadtree.x - q.width and q.y == quadtree.y]),
                                 None)




# Could only call this if the quadtree has > 1 block inside it. No need for detection if only 1 block.
    def recursive_update_quadtrees(self, quadtree):
        self.all_quads.append(quadtree)
        if quadtree.branch_count < 3:  # not a leaf
            quadtree.create_branches(branch_count=quadtree.branch_count)
            for child in quadtree.children:
                for block in self.blocks:
                    if self.check_block_in_quad(block, child):
                        self.recursive_update_quadtrees(quadtree=child)
                        break
        else:  # leaf
            for block in self.blocks:
                self.add_rects_to_quadtree(block=block, quadtrees=[quadtree])


    def get_neighbors(self, quadtree):
        return quadtree.get_neighbors()


    def get_update_neighbors(self, quadtree):
        if quadtree in self.q_neighbors:
            return self.q_neighbors[quadtree]
        neighbors = quadtree.get_neighbors()
        self.q_neighbors[quadtree] = neighbors
        return neighbors


    def check_block_in_quad(self, block, quadtree):
        if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
            and quadtree.y >= block.rect.centery >= quadtree.y - quadtree.height:
                return True
        else: return False


    def add_rects_to_quadtree(self, block, quadtrees: list[Quadtree]):
        for quadtree in quadtrees:
            # if self.check_block_in_quad(block, quadtree):
            quadtree.objects.append(block)
            block.quadtree = quadtree
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
    def update_block_quadtree(self, block) -> None:  # , y_count: int, x_count: int
        # TODO: some blocks do not properly exit their quadtrees. The tree still has objects in its list
        # slower :(   32 fps lowest vs 39 fps
        # block.quadtree.objects.remove(block)
        # x_index = math.floor(block.rect.centerx / x_count)
        # y_index = math.floor(block.rect.centery / y_count)
        # tree = self.tree_org[y_index][x_index]
        # tree.objects.append(block)
        # block.quadtree = tree
        # return

        try:
            x_change = block.rect.centerx - block.quadtree.x
            y_change = block.rect.centery - block.quadtree.y
        except:
            return

        if y_change > block.quadtree.height and block.quadtree.south:
            block.quadtree.south.objects.append(block)
            block.quadtree = block.quadtree.south
            block.quadtree.objects.remove(block)
        elif x_change < 0 and block.quadtree.west:
            block.quadtree.west.objects.append(block)
            block.quadtree = block.quadtree.west
            block.quadtree.objects.remove(block)
        elif x_change > block.quadtree.width and block.quadtree.east:
            block.quadtree.east.objects.append(block)
            block.quadtree = block.quadtree.east
            block.quadtree.objects.remove(block)
        elif y_change < 0 and block.quadtree.north:  # assign north
            block.quadtree.north.objects.append(block)
            block.quadtree = block.quadtree.north
            block.quadtree.objects.remove(block)