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
            block.update(screen)



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