import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg

gravity = 9.8
terminal_velocity = 26


# to improve processing efficiency, divide screen into grid & only pass in blocks in same + neighboring grids
# or, pass in any blocks that are within x distance of the block. WOuld involve looping thorugh all blocks
def check_collision(object: pg.Rect, # object_position: (int, int),
                    blocks: list[pg.Rect]) -> bool:
        #-> dict[str, Block_Type]:
    for block in blocks:
        if block == object:
            continue
        # if object.colliderect(block):
        #     return True
        if block.top == object.bottom:
            return True

    return False


# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

def get_neighboring_rects(object: pg.Rect):
    pass