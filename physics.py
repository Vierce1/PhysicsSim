import Blocks.block_type as block_type
from Blocks.block_type import *
from Blocks import block
import pygame as pg


gravity = 9.8
terminal_velocity = 26
display_res = []
ground = 1100

# to improve processing efficiency, divide screen into grid & only pass in blocks in same + neighboring grids
# or, pass in any blocks that are within x distance of the block. WOuld involve looping thorugh all blocks
def check_collision(block, rects: list[pg.Rect]) -> bool:
    for rect in rects:
        if rect == block:
            continue
        # if block.colliderect(object):
        #     return True
        if rect.top == block.rect.bottom and abs(rect.x - block.rect.x) < 10:
                #and block.y > object.y:
            return True
    if block.rect.y + block.rect.height >= ground:
        block.grounded = True
        return True

    return False

# stop blocks from running collision once on the ground?

# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

