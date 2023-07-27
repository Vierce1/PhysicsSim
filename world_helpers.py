import math
from scipy import spatial
from numba import jit
import numpy as np


def check_dist(pos_1: (int, int), pos_2: (int, int)) -> int:
    return round(math.dist(pos_1, pos_2))

def get_blocks_in_dist(pos: (int, int), block_list: set, distance: int) -> set:
    blocks = set()
    for block in block_list:
        # dist = (block.position[0] - pos[0])**2 + (block.position[1] - pos[1])**2 < distance**2
        dist = math.sqrt((block.position[0] - pos[0])**2 + (block.position[1] - pos[1])**2)
        if dist < distance:
            blocks.add(block)
    return blocks

# @jit(nopython=True)  # No improvement vs compiling pre
def get_scaled_pos(position: (int, int), world_offset: (int, int), screen_width: int, render_width: int,
                   screen_height: int, render_height: int) -> (int, int):
    ratio_x = (screen_width / render_width)
    ratio_y = (screen_height / render_height)
    converted_pos = (round(position[0] / ratio_x + world_offset[0]), round(position[1] / ratio_y + world_offset[1]))
    return converted_pos


# Slower than using scipy c_dist
# def get_dist(p1: (int, int), m2: []):
#     m2 = np.array(m2)
#     dists = []
#     for p2 in m2:
#         dists.append(get_c_dist(p1[0], p1[1], p2[0], p2[1]))
#     # dists = spatial.distance.cdist(m1, m2)
#     return dists
#
# @jit(nopython=True)
# def get_c_dist(p1x: int, p1y: int, p2x: int, p2y: int):
#     return (p2x - p1x)**2 + (p2y - p1y)**2
