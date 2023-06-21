# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
# import Blocks.block as block
from Blocks import block
from quadtree import Quadtree
import pygame as pg

class Terrain_Manager:
    def __init__(self):
        pass

    blocks = []
    block_rects = []


    def update(self, screen):
        for block in self.blocks:

            block.update(screen=screen)



# improvement: 1 option = only calling this for blocks with collision_detection = True
# option 2 = starting with the Quadtree and only passing in blocks that are close + collision detection
    def add_rect_to_quadtree(self, block, quadtrees: list[Quadtree]):
        for quadtree in quadtrees:
            if quadtree.x <= block.rect.centerx <= quadtree.x + quadtree.width \
              and quadtree.y <= block.rect.centery <= quadtree.y + quadtree.height:
                quadtree.objects.append(block)
                block.quadtree = quadtree

# This ended up being slightly slower:
#     def add_rects_to_quadtree(self, quadtree: Quadtree, moving_blocks: list):
#         for block in moving_blocks:
#             if quadtree.x <= block.rect.x <= quadtree.x + quadtree.width \
#               and quadtree.y <= block.rect.y <= quadtree.y + quadtree.height:
#                     quadtree.objects.append(block.rect)
#                     block.quadtree = quadtree


    def update_block_quadtree(self, block):
        x_change = block.rect.centerx - block.quadtree.x
        y_change = block.rect.centery - block.quadtree.y

        if x_change < 0 or x_change > block.quadtree.width \
            or y_change < 0 or y_change > block.quadtree.height:
            # no longer inside the quadtree. assign it to the new one
                try:
                    block.quadtree.objects.remove(block)
                except:
                    block.quadtree.objects = [b for b in block.quadtree.objects if b != block]
                if y_change > 0 and block.quadtree.south:  # assign south
                    block.quadtree.south.objects.append(block)
                    block.quadtree = block.quadtree.south
                elif x_change < 0 and block.quadtree.west:  # assign west
                    block.quadtree.west.objects.append(block)
                    block.quadtree = block.quadtree.west
                elif x_change > 0 and block.quadtree.east:  # assign east
                    block.quadtree.east.objects.append(block)
                    block.quadtree = block.quadtree.east
                elif y_change < 0 and block.quadtree.north:  # assign north
                    block.quadtree.north.objects.append(block)
                    block.quadtree = block.quadtree.north

