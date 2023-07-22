# import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks.block import Block
import Blocks.terrain_manager as tm
import math
import random
from scipy.stats import uniform


class Terrain_Gen:
    def __init__(self, terrain_manager):
        self.terrain_manager = terrain_manager


#TODO: Draw a poly and fill it with blocks
    def gen_terrain(self, block_count: int, block_type: str, bounds: (int, int, int, int)) -> list[Block]:
        pixel_count = (bounds[1] - bounds[0]) * (bounds[3] - bounds[2])
        if block_count / pixel_count < 1:  # particles do not fill entire bounds
            return list(self.uniform(block_count, block_type, bounds))
        else:  # particles fill exactly bounds. Note can pass in 999999 as block count to force the fill method
            # print('fill bounds') # Pass in pixel_count to avoid over-generation
            return list(self.fill_bounds(pixel_count, block_type, bounds))

    def fill_bounds(self, block_count: int, block_type: str, bounds: (int, int, int, int)) -> set[Block]:
        generated_blocks = set()
        for y in range(bounds[2], bounds[3]):
            for x in range(bounds[0], bounds[1]):
                pos = (x, y)
                type_object = Block_Type().get_block_type(block_type)
                block = Block(type_object, pos)
                if block.type.start_static:  # allow blocks like sand to start grounded after 1 frame (drawing)
                    block.collision_detection = False
                generated_blocks.add(block)
                self.terrain_manager.matrix[x, y] = 1   # correct index passed in after all blocks created

        return generated_blocks



    def uniform(self, block_count: int, block_type: str, bounds: (int, int, int, int)) -> set[Block]:
        generated_blocks = set()
        xs = uniform.rvs(loc=bounds[0], scale=bounds[1] - bounds[0], size=block_count)
        ys = uniform.rvs(loc=bounds[2], scale=bounds[3] - bounds[2], size=block_count)
        x = bounds[0]
        y = bounds[2]
        for x, y in zip(xs, ys):
            pos = (round(x), round(y))
            if self.terrain_manager.matrix[pos[0], pos[1]] == 1:
                continue
            type_object = Block_Type().get_block_type(block_type)
            block = Block(type_object, pos)
            if block.type.start_static:
                block.collision_detection = False
            generated_blocks.add(block)
            self.terrain_manager.matrix[pos[0], pos[1]] = 1  # correct index passed in after all blocks created

        return generated_blocks


    def pick_color(self, length: int) -> int:
        return random.randrange(length)
