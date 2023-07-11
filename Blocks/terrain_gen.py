import math

import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks.block import Block
import Blocks.terrain_manager as tm
import random
import math


randomness = (0, 3)
def gen_terrain(block_count: int, block_type: Block_Type, bounds: (int, int, int, int),
                terrain_manager: tm.Terrain_Manager)-> list[Block]:
    generated_blocks = []
    blocks_per_row = math.ceil(block_count / ((bounds[1] - bounds[0]) / (bounds[3] - bounds[2])))
    x_step = round((bounds[1] - bounds[0]) / blocks_per_row)
    print(f'blocks per row: {blocks_per_row}')
    print(f'x_step: {x_step}')
    x = bounds[0]
    y = bounds[2]
    for i in range(block_count):
        block = Block(block_type, (x, y))
        generated_blocks.append(block)
        next_x = x_step + random.randrange(randomness[0], randomness[1])
        if next_x == x:
          next_x = x + x_step
        else:
            x += next_x
        if x >= bounds[1]:
            y += 1
            x = bounds[0]
        if y >= bounds[3]:
            break

    # for y in range(bounds[2], bounds[3]):
    #     for x in range(bounds[0], bounds[1], x_step):
    #         block = Block(block_type, (x, y))
    #         generated_blocks.append(block)


    # for i in range(block_count):
    #     coord_x, coord_y = get_random_coords(x_bounds=(bounds[0], bounds[1]),   \
    #                                 y_bounds=(bounds[2], bounds[3]), prev_blocks=generated_blocks)
    #
    #     block = Block(block_type, (coord_x, coord_y))
    #     generated_blocks.append(block)

    return generated_blocks






def get_random_coords(x_bounds: (int, int), y_bounds: (int, int), prev_blocks: list[Block]) -> (int, int):
    coord_x = random.randrange(x_bounds[0], x_bounds[1])
    coord_y = random.randrange(y_bounds[0], y_bounds[1])
    loop_break = 0
    while len([b for b in prev_blocks if abs(b.position[0] - coord_x) < b.width
                and abs(b.position[0] - coord_y) < b.width]) > 0:
        coord_x = random.randrange(x_bounds[0], x_bounds[1])
        coord_y = random.randrange(y_bounds[0], y_bounds[1])
        loop_break += 1
        if loop_break > 5:
            break
    return coord_x, coord_y