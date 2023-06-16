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



    def add_rect_to_quadtree(self, block, quadtrees: list[Quadtree]):
        for quadtree in quadtrees:
            if block.rect.x <= quadtree.x + quadtree.width and block.rect.x >= quadtree.x \
              and block.rect.y <= quadtree.y + quadtree.height and block.rect.y >= quadtree.y:
                quadtree.objects.append(block.rect)
                block.quadtree = quadtree
