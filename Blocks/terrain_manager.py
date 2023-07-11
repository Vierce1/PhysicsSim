# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
import physics
import pymorton
# import Blocks.block as block
from Blocks import block
import pygame as pg
import math
import physics
from pymorton import *
import sys
import size_checker


class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        # self.all_quads = []# set()
        # self.node_count = 1  # for root node
        self.blocks = set()
        # self.block_rects = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        # self.max_branches = 10
        # self.capacity = 35
        # self.root_quadtree = Quadtree(x=0, y=0 + self.screen_height,
        #                          width=self.screen_width, height=self.screen_height, branch_count=0)
        # self.all_quads.append(self.root_quadtree)  #add(self.root_quadtree)
        physics.t_m = self
        # self.max_collision_dist = 0 # should be about 1.5x diameter of block
        # self.total_col_dets = 0
        self.render_image = None
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.matrix = {}
        for x in range(screen_width):  # initalize all spaces as empty
            for y in range(screen_height):
                self.matrix[x,y] = 0



    def setup(self, render_image):  # need new method for adding blocks after init
        # [self.set_index(block=b, index=self.blocks.index(b)) for b in self.blocks]
        # block = Blocks.block.Block(Blocks.block_type.Sand(), (0, 0))
        # self.max_collision_dist = 2 * block.rect.width
        for b in self.blocks:
            self.matrix[b.rect.x, b.rect.y] = 1
        self.render_image = render_image


    # def set_index(self, block, index: int):
    #     block.id = index



    # @profile
    def update(self, screen) -> list:
        for block in self.blocks:
            physics.update(block=block, screen=self.render_image)





#TODO: Major memory usage functions:



