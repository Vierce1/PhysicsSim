import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks.block import Block
import Blocks.terrain_manager as tm
import random


def gen_terrain(block_list: (int, Block_Type), bounds: (int, int, int, int),
                terrain_manager: tm.Terrain_Manager)-> list[Block]:
    generated_blocks = []
    for _ in range(block_list[0]):
        coord_x, coord_y = get_random_coords(x_bounds=(bounds[0], bounds[1]),   \
                                    y_bounds=(bounds[2], bounds[3]), prev_blocks=generated_blocks)

        block = Block(block_list[1], (coord_x, coord_y))
        generated_blocks.append(block)
    return generated_blocks


def get_random_coords(x_bounds: (int, int), y_bounds: (int, int), prev_blocks: list[Block]):
    coord_x = random.randrange(x_bounds[0], x_bounds[1])
    coord_y = random.randrange(y_bounds[0], y_bounds[1])
    loop_break = 0
    while len([b for b in prev_blocks if abs(b.rect.x - coord_x) < b.rect.width
                and abs(b.rect.y - coord_y) < b.rect.height]) > 0:
        coord_x = random.randrange(x_bounds[0], x_bounds[1])
        coord_y = random.randrange(y_bounds[0], y_bounds[1])
        loop_break += 1
        if loop_break > 5:
            break
    return coord_x, coord_y