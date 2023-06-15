import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks.block import Block
import random


def gen_terrain(block_list: (int, Block_Type), bounds: (int, int, int, int)) -> list[(Block, (int, int))]:
    generated_blocks = []
    for _ in range(block_list[0]):
        coord_x = random.randrange(bounds[0], bounds[1])
        coord_y = random.randrange(bounds[2], bounds[3])
        generated_blocks.append((Block(block_list[1]), (coord_x, coord_y)))
    return generated_blocks