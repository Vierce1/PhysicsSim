# import Blocks.block_type as block_type
# from Blocks.block_type import *
import Blocks.block_type
# import Blocks.block as block
from Blocks import block

class Terrain_Manager:
    def __init__(self):
        pass

    blocks = []
    block_rects = []


    def update(self, screen):
        for block in self.blocks:
            block.update(screen)


