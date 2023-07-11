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


class Terrain_Manager:
    def __init__(self, screen_width: int, screen_height: int):
        self.blocks = set()
        self.screen_width = screen_width
        self.screen_height = screen_height
        physics.t_m = self
        self.render_image = None
        # print(f'block size: {sys.getsizeof(Blocks.block.Block)}')
        self.matrix = {}
        for x in range(screen_width):  # initalize all spaces as empty
            for y in range(screen_height):
                self.matrix[x,y] = 0
        print(f'matrix length: {len(self.matrix)}')



    def setup(self, render_image):  # need new method for adding blocks after init
        for b in self.blocks:
            self.matrix[b.position[0], b.position[1]] = 1
        self.render_image = render_image


    # @profile
    def update(self, screen) -> list:
        for block in self.blocks:
            physics.update(block=block, screen=self.render_image)





#TODO: Major memory usage functions:



