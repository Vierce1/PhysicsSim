# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree
import pygame as pg
import math

class Terrain_Manager:
    def __init__(self):
        self.quadtrees = []
        self.blocks = []
        self.block_rects = []
        # 2d array representing the spatials organization of the quadtrees. Used to quickly assess block location
        self.tree_org = []
        # New idea: first block that builds quadtree nieghbors sends the list here
        self.q_neighbors = dict()

    # def organize_trees(self, quadtrees: list[Quadtree]):
    #     for tree in quadtrees:
    #         if tree.x == 0.0:
    #             self.tree_org.append([])
    #         self.tree_org[-1].append(tree)
    #     # trees now arranged in 2d array of size y_count * x_count



    def update(self, screen):
        self.q_neighbors = dict()
        # Updated to this, fixes FPS. No longer have object list being cleared and recreated every frame
        # Only blocks that leave their quadtree look for new ones.
        [self.update_block_quadtree(block=block)
         for block in self.blocks if block.collision_detection]  # and block.quadtree

        for block in self.blocks:
            block.update(screen=screen)



    def get_update_neighbors(self, quadtree):
        if quadtree in self.q_neighbors:
            return self.q_neighbors[quadtree]
        neighbors = quadtree.get_neighbors()
        self.q_neighbors[quadtree] = neighbors
        return neighbors


    def add_rect_to_quadtree(self, block, quadtrees: list[Quadtree], y_count: int, x_count: int):
        # Only called on block spawn
        for quadtree in quadtrees:
            if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
              and quadtree.y >= block.rect.centery >= quadtree.y - quadtree.height:
                quadtree.objects.append(block)
                block.quadtree = quadtree
            self.quadtrees.append(quadtree)
        # new method: place blocks in tree based on x,y and self.tree_org indices
        # x_index = math.floor(block.rect.centerx / x_count)
        # y_index = math.floor(block.rect.centery / y_count)
        # tree = self.tree_org[y_index][x_index]
        # tree.objects.append(block)
        # block.quadtree = tree



# improvement: 1 option = only calling this for blocks with collision_detection = True
  # option 2 = starting with the Quadtree and only passing in blocks that are close + collision detection
    # Called every frame for blocks with collision detection True
    def update_block_quadtree(self, block) -> None:  #, y_count: int, x_count: int
#TODO: some blocks do not properly exit their quadtrees. The tree still has objects in its list
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
        elif x_change < 0 and block.quadtree.west:
            block.quadtree.west.objects.append(block)
            block.quadtree = block.quadtree.west
        elif x_change > block.quadtree.width and block.quadtree.east:
            block.quadtree.east.objects.append(block)
            block.quadtree = block.quadtree.east
        elif y_change < 0 and block.quadtree.north:  # assign north
            block.quadtree.north.objects.append(block)
            block.quadtree = block.quadtree.north

        #
        # if x_change < 0 or x_change > block.quadtree.width \
        #     or y_change < 0 or y_change > block.quadtree.height:
        #     # no longer inside the quadtree. assign it to the new one
        #         try:
        #             block.quadtree.objects.remove(block)
        #         except: pass
        #     #     block.quadtree.objects = [b for b in block.quadtree.objects if b != block]
        #         if y_change > 0 and block.quadtree.south:  # assign south
        #             block.quadtree.south.objects.append(block)
        #             block.quadtree = block.quadtree.south
        #         elif x_change < 0 and block.quadtree.west:  # assign west
        #             block.quadtree.west.objects.append(block)
        #             block.quadtree = block.quadtree.west
        #         elif x_change > 0 and block.quadtree.east:  # assign east
        #             block.quadtree.east.objects.append(block)
        #             block.quadtree = block.quadtree.east
        #         elif y_change < 0 and block.quadtree.north:  # assign north
        #             block.quadtree.north.objects.append(block)
        #             block.quadtree = block.quadtree.north
