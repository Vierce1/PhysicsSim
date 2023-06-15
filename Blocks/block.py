import Blocks.block_type as block_type
from Blocks.block_type import *


class Block:
    def __init__(self, type: Block_Type):
        self.type = type
        # self.type.__init__(self.type)