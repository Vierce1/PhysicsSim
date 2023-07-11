import math
import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks.block import Block
import Blocks.terrain_manager as tm
import random
import numpy as np
from scipy.stats import uniform


randomness = (0, 3)
def gen_terrain(block_count: int, block_type: Block_Type, bounds: (int, int, int, int),
                terrain_manager: tm.Terrain_Manager)-> list[Block]:
    generated_blocks = []
    xs = uniform.rvs(loc=bounds[0], scale=bounds[1]-bounds[0], size=block_count)
    ys = uniform.rvs(loc=bounds[2], scale=bounds[3]-bounds[2], size=block_count)
    x = bounds[0]
    y = bounds[2]
    for x, y in zip(xs, ys):
        block = Block(block_type, (round(x), round(y)))
        generated_blocks.append(block)

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