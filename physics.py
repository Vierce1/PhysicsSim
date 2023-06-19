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
        # if rect.top == block.rect.bottom \
        if abs(rect.top - block.rect.bottom) < rect.height * 0.25 \
            and abs(rect.x - block.rect.x) < block.rect.width * 1.5:
                #and block.y > object.y: # not needed?
            # move the block back 1 frame so they aren't occluded
            block.rect.y = rect.y - rect.height
            return True
    if block.rect.y + block.rect.height >= ground:  # block is at ground level, stop detecting collision
        block.collision_detection = True
        return True

    return False

# stop blocks from running collision once on the ground?

# alternate methods:
  # Every block seeds its position to a master list
  # Run through the positions moving left->right, bottom->top
  # if there is a block in the checked position, check if it has a block beneath it
  # if so, flip a bool in the block

